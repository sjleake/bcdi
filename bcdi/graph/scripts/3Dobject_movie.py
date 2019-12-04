# -*- coding: utf-8 -*-

# BCDI: tools for pre(post)-processing Bragg coherent X-ray diffraction imaging data
#   (c) 07/2017-06/2019 : CNRS UMR 7344 IM2NP
#   (c) 07/2019-present : DESY PHOTON SCIENCE
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage.measurements import center_of_mass
import matplotlib.animation as manimation
import tkinter as tk
from tkinter import filedialog
import matplotlib.ticker as ticker
import sys
sys.path.append('//win.desy.de/home/carnisj/My Documents/myscripts/bcdi/')
import bcdi.postprocessing.postprocessing_utils as pu
import bcdi.graph.graph_utils as gu

helptext = """
Create a movie from a 3D real space reconstruction in each direction.
"""

scan = 22
root_folder = 'D:/data/P10_August2019/data/'  # location of the .spec or log file
sample_name = "gold_2_2_2_000"  # "SN"  #
datadir = root_folder + sample_name + str(scan) + '/pynx/800_800_800_1_1_1/'
comment = ''  # should start with _
movie_z = True  # save movie along z axis (downstream)
movie_y = True  # save movie along y axis (vertical up)
movie_x = True  # save movie along x axis (outboard)
frame_spacing = 2  # spacing between consecutive slices in voxel
vmin_vmax = [0, 1]  # scale for plotting the data
roi = []  # ROI to be plotted, leave it as [] to use all the reconstruction [zstart, ztop, ystart, ystop, xstart, xstop]
field_name = ''  # name or ''
# load the field name in a .npz file, if '' load the complex object and plot the normalized modulus
threshold = 0.05  # threshold apply on the object, if np.nan nothing happens
##################################
# end of user-defined parameters #
##################################

###################
# define colormap #
###################
colormap = gu.Colormap()
my_cmap = colormap.cmap

###############
# load FFMpeg #
###############
try:
    FFMpegWriter = manimation.writers['ffmpeg']
except KeyError:
    print('KeyError: \'ffmpeg\'')
    sys.exit()
except RuntimeError:
    print("Could not import FFMpeg writer for movie generation")
    sys.exit()

#############################
# load reconstructed object #
#############################
plt.ion()
root = tk.Tk()
root.withdraw()

if len(field_name) == 0:
    file_path = filedialog.askopenfilename(initialdir=datadir, title="Select the reconstructed object",
                                           filetypes=[("NPZ", "*.npz"), ("NPY", "*.npy"),
                                                      ("CXI", "*.cxi"), ("HDF5", "*.h5")])
    obj, extension = pu.load_reconstruction(file_path)
    obj = abs(obj)
    obj = obj / obj.max()
    if extension == '.h5':
        comment = comment + '_mode'
else:
    file_path = filedialog.askopenfilename(initialdir=datadir, title="Select the reconstructed object",
                                           filetypes=[("NPZ", "*.npz")])
    obj = np.load(file_path)[field_name]
nbz, nby, nbx = obj.shape

#################
# rotate object #
#################
new_shape = [int(1.2*nbz), int(1.2*nby), int(1.2*nbx)]
obj = pu.crop_pad(array=obj, output_shape=new_shape, debugging=False)
nbz, nby, nbx = obj.shape

print("Cropped/padded object size before rotating: (", nbz, ',', nby, ',', nbx, ')')
print('Rotating object to have the crystallographic axes along array axes')
axis_to_align = np.array([0.2, 1, 0.02])  # in order x y z for rotate_crystal()
obj = pu.rotate_crystal(array=obj, axis_to_align=axis_to_align, reference_axis=np.array([0, 1, 0]),
                        debugging=True)  # out of plane alignement
axis_to_align = np.array([1, 0, -0.1])  # in order x y z for rotate_crystal()
obj = pu.rotate_crystal(array=obj, axis_to_align=axis_to_align, reference_axis=np.array([1, 0, 0]),
                        debugging=True)  # inplane alignement

###################
# apply threshold #
###################
if not np.isnan(threshold):
    obj[obj < threshold] = 0

#############
# check ROI #
#############
if len(roi) == 6:
    print('Crop/pad the reconstruction to accommodate the ROI')
    obj = pu.crop_pad(array=obj, output_shape=[roi[1]-roi[0], roi[3]-roi[2], roi[5]-roi[4]])

#################
# movie along z #
#################
if movie_z:
    metadata = dict(title='S'+str(scan)+comment)
    writer = FFMpegWriter(fps=5, metadata=metadata)
    fontsize = 10

    fig = plt.figure()
    with writer.saving(fig, datadir+"S"+str(scan)+"_z_movie.avi", dpi=100):
        for index in range(nbz // frame_spacing):
            img = obj[index*frame_spacing, :, :]
            plt.clf()
            plt.imshow(img, vmin=vmin_vmax[0], vmax=vmin_vmax[1], cmap=my_cmap)
            ax = plt.gca()
            ax.invert_yaxis()
            ax.set_title("slice # %3d" % index, fontsize=fontsize)
            writer.grab_frame()

#################
# movie along y #
#################
if movie_y:
    metadata = dict(title='S'+str(scan)+comment)
    writer = FFMpegWriter(fps=5, metadata=metadata)
    fontsize = 10

    fig = plt.figure()
    with writer.saving(fig, datadir+"S"+str(scan)+"_y_movie.avi", dpi=100):
        for index in range(nby // frame_spacing):
            img = obj[:, index*frame_spacing, :]
            plt.clf()
            plt.imshow(img, vmin=vmin_vmax[0], vmax=vmin_vmax[1], cmap=my_cmap)
            ax = plt.gca()
            ax.invert_yaxis()
            ax.set_title("slice # %3d" % index, fontsize=fontsize)
            writer.grab_frame()

#################
# movie along x #
#################
if movie_x:
    metadata = dict(title='S'+str(scan)+comment)
    writer = FFMpegWriter(fps=5, metadata=metadata)
    fontsize = 10

    fig = plt.figure()
    with writer.saving(fig, datadir+"S"+str(scan)+"_x_movie.avi", dpi=100):
        for index in range(nbx // frame_spacing):
            img = obj[:, :, index*frame_spacing]
            plt.clf()
            plt.imshow(img, vmin=vmin_vmax[0], vmax=vmin_vmax[1], cmap=my_cmap)
            ax = plt.gca()
            ax.invert_yaxis()
            ax.set_title("slice # %3d" % index, fontsize=fontsize)
            writer.grab_frame()