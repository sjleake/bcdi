"""
doit configuration for BCDI
"""

import coverage
import os
import shutil

# Generic functions go here


def get_path():
    """Get the path of the dodo.py file."""
    return os.path.dirname(os.path.abspath(__file__))


def get_version():
    with open("bcdi/__init__.py", "r") as version_file:
        version = version_file.readlines()[-1].split("=")[1].strip().split('"')[1]
    return version


# Tasks go here


def task_black():
    """Run black against the package."""
    path = get_path()
    return {
        "actions": [f"python -m black --line-length=88 {path}"],
        "verbosity": 2,
    }


def task_clean_dist():
    """Remove the build directory and its content."""

    def delete_dir(dirname):
        path = os.path.join(get_path(), dirname).replace("\\", "/")
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"\n\tDeleted {path}\n")
        else:
            print("\n\tNo build directory to delete.\n")

    return {
        "actions": [(delete_dir, ["dist/"])],
        "verbosity": 2,
    }


def task_clean_doc():
    """Remove the compiled documentation."""

    def delete_dir(dirname):
        path = os.path.join(get_path(), dirname).replace("\\", "/")
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"\n\tDeleted {path}\n")
        else:
            print("\n\tNo built documentation to delete.\n")

    return {
        "actions": [(delete_dir, ["doc/doc_html/"])],
        "verbosity": 2,
    }


def task_code_style():
    """Run pycodestyle on the modules."""
    return {
        "actions": [
            "pycodestyle    bcdi --max-line-length=88 "
            "--ignore=E24,E121,E123,E126,E203,E226,E704,W503"
        ],
        "verbosity": 2,
    }


def task_coverage_xml():
    """
    Generate an XML version of the coverage report.

    It can be opened with Notepad++.
    """

    def create_coverage_xml(coverage_file, output_file):
        print("\n\tXML coverage report generated in 'test_output/'\n")
        cov = coverage.Coverage(data_file=coverage_file)
        cov.load()
        cov.xml_report(outfile=output_file)

    return {
        "actions": [
            (create_coverage_xml, [".coverage", "test_output/coverage-report.xml"])
        ],
        "file_dep": [".coverage"],
        "targets": ["test_output/coverage-report.xml"],
        "verbosity": 2,
    }


def task_clean_coverage():
    """Delete the coverage report."""

    def delete_coverage(filename):
        path = os.path.join(get_path(), filename).replace("\\", "/")
        if os.path.isfile(path):
            os.unlink(path)
            print(f"\n\tDeleted {path}\n")
        else:
            print("\n\tNo coverage file to delete.\n")

    return {
        "actions": [(delete_coverage, [".coverage"])],
        "file_dep": ["test_output/coverage-report.xml"],
        "verbosity": 2,
    }


def task_docstrings():
    """Run pydocstyle on the modules."""
    return {
        "actions": ["pydocstyle bcdi --ignore=D107,D212,D203"],
        "verbosity": 2,
    }


def task_tests():
    """Run unit tests with coverage."""
    return {
        "actions": [f"coverage run --source=bcdi -m unittest discover"],
        "targets": [".coverage"],
        "verbosity": 2,
    }


def task_build_doc():
    """Build the documentation with sphinx."""
    # import pathlib
    # documentation_sources = list(pathlib.Path("doc").glob("**/*"))
    # print(documentation_sources)
    return {
        "actions": ["sphinx-build doc doc/doc_html"],
        "targets": ["docs/"],
    }


def task_build_distribution():
    """Build the distribution."""
    return {
        "actions": ["python setup.py sdist bdist_wheel"],
        "targets": [f"dist/bcdi-{get_version()}.tar.gz"],
        "verbosity": 1,
    }


def task_check_description():
    """Check whether the long description will render correctly on PyPI."""
    return {
        "actions": ["twine check dist/*"],
        "file_dep": [f"dist/bcdi-{get_version()}.tar.gz"],
        "verbosity": 2,
    }