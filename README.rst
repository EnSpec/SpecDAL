Visit our `ReadTheDocs <http://specdal.readthedocs.io/en/latest/>`_.

Introduction
============

``specdal`` is a Python package for loading and manipulating field
spectroscopy data. It currently supports readers for ASD, SVC, and PSR
spectrometers. ``specdal`` provides useful functions and command line
scripts for processing and aggregating the data.

Features
========

1. Command line interface

   - specdal_info: lightweight script to read and display content of
     spectral files
     
   - specdal_pipeline: default script to convert spectral files into
     datasets and figures

2. Python interface
   
   - readers for .asd, .sig, .sed spectral files
     - Pico files (WIP)

   - spectral functions that operate on pandas objects
     
     - interpolation
       
     - jump_correction
       
     - joining proximal measurements (WIP)
     
   - ``Spectrum`` and ``Collection`` classes which wrap around pandas
     objects to provide simpler interface for spectral functions

3. GUI (under development)
   
Tutorials
=========

See the Jupyter notebooks `here
<https://github.com/EnSpec/SpecDAL/tree/master/specdal/examples/>`_.


Installation
============

SpecDAL can be installed from PyPI using pip. For a more detailed
walkthrough, see
`http://specdal-test.readthedocs.io/en/latest/installation.html`

Installation from Source
========================

**Warning:** This method of installation will override any other versions of SpecDAL
in your current environment. A virtual environment can be used to preserve other installations.

SpecDAL can also be installed from source.  Open a terminal and run the command:

``git clone https://github.com/EnSpec/SpecDAL.git && pip install SpecDAL/`` 

The SpecDAL python package and ``specdal_pipeline`` command-line tool will be
installed on your system (see ``specdal_pipeline --help`` for usage).


Example Usage
=============

For a description of all command line arguments: ``specdal_pipeline --help``.

To produce an individual plot and textfile for every spectrum file 
in directory ``/path/to/spectra/`` and store the results in ``specdal_output/``:

``specdal_pipeline  -o specdal_output /path/to/spectra/``

To only output whole-dataset images and files:

``specdal_pipeline  -oi -o specdal_output /path/to/spectra/``

To only output images, with no data files:

``specdal_pipeline  -od -o specdal_output /path/to/spectra/``


To group input files by the first 3 underscore-separated components 
of their filename (such that ``foo_bar_baz_001.asd`` and 
``foo_bar_baz_002.asd`` will appear in one group, and
``foo_bar_qux_001.asd`` in another):

``specdal_pipeline -g -gi 0 1 2 -- /path/to/spectra/``

To also output the mean and median of every group of spectra:

``specdal_pipeline -g -gi 0 1 2  -gmean -gmedian /path/to/spectra/``

To remove all white reference spectra from the output dataset (leaves input files intact):

``specdal_pipeline --filter_white /path/to/spectra/``

To remove all white reference spectra from the dataset, as well as spectra
with a 750-1200 nm reflectance that is greater than 1 standard deviation from the mean,
or with a 500-600 nm reflectance that is greater than 2 standard devations from the mean:

``specdal_pipeline --filter_white --filter_std 750 1200 1 500 600 2  -- /path/to/spectra/``

To perform the filtering above, and then group the remaining spectra by filename:

``specdal_pipeline --filter_white --filter_std 750 1200 1 500 600 2 
-g -gi 0 1 2 /path/to/spectra/``

To group the spectra by filename, and then perform filtering on each group:

``specdal_pipeline --filter_white --filter_std 750 1200 1 500 600 2 
-g -gi 0 1 2  --filter_on group /path/to/spectra/``

Usage with Docker
=================

Steps:

- Download and save the files in the directory which has all the folders or files you want to process..

- Download and install docker software from: https://www.docker.com/get-started

- Run the following in terminal from directory where the Dockerfile and runDocker are stored

``docker build -t specdal --no-cache -f Dockerfile .``

``bash runDocker``

That will take you inside the docker called 'specdal' where you can run ``specdal_pipeline`` command as shown in the example usage above. Your current directory on the laptop will get mapped to ``/home/`` in the docker.

Once the image is built, the next time only ``bash runDocker`` command can be run to go inside the docker. Building the image will take some time, and it will require 1.4GB space approximately.
