from glob import glob
from os.path import splitext, basename

from setuptools import setup, find_packages


def get_version():
    """Read version from CHANGELOG.md. Defaults to unknown"""
    try:
        with open("CHANGELOG.md") as f:
            version = f.readline().split(" ")[1]
            return version
    except:
        return "unknown"

def get_list_requirements():
    """Read requirements.txt"""
    with open("requirements.txt") as f:
        lns = f.readlines()
        lns = [ln for ln in lns if "#" not in ln]
        return lns

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pyconfita",
    version=get_version(),
    description="Confita-like library",
    url="https://github.com/birotaio/data-confita.git",
    packages=find_packages('src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8, <3.9",
    install_requires=get_list_requirements(),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
)
