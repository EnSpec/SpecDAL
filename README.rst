Introduction
============

``specdal`` is a Python package for loading and manipulating field
spectroscopy data. It currently supports readers for ASD, SVC, and PSR
spectremeters. ``specdal`` provides useful functions and command line
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
     objects to provide simpler interface
     
Tutorials
=========

See the Jupyter notebooks in (PROVIDE A LINK HERE).


Installation
============

Prerequisite
------------

1. Setup virtualenv (recommended)

   ::

      $ pip install --user virtualenv
      $ mkdir ~/venv
      $ virtualenv -p python3 ~/venv/specdal
      $ source ~/venv/specdal/bin/activate
      
      $ ... # install/use specdal
      
      $ deactivate

Via pip
-------

1. Install Python 3

   ::
      
      $ pip3 install specdal --upgrade


Development version
-------------------

1. Open terminal or Git-bash and navigate to the desired directory using
   ``cd <directory>``.
2. The following command will create a directory ``SpecDAL``
   containing ``SpecDAL``:

   ::

      $ git clone https://github.com/EnSpec/SpecDAL.git
      $ cd SpecDAL
      
3. To update the package, go to ``SpecDAL`` directory and run the
   following command:

   ::

       $ git pull origin master

4. To install ``specdal`` in development mode

   ::
      
      $ source ~/venv/specdal/bin/activate # recommended (see virtualenv section)
      $ pip3 install -r requirements.txt
      $ python setup.py develop
      
      $ ... # edit and test specdal
      
      $ python setup.py develop --uninstall

