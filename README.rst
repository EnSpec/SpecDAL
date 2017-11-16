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
