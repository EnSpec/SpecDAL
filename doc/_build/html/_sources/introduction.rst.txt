============
Introduction
============

SpecDAL is a Python package for loading and manipulating field
spectroscopy data. It currently supports readers for ASD, SVC, and PSR
spectrometers. SpecDAL provides useful functions and command line
scripts for processing and aggregating the data.

Interface
=========

There are three options for using SpecDAL.

1. Python interface

   The lowest level interface is for users to import ``specdal`` as a
   Python module.  Functions in ``specdal`` are written to operate
   directly on Pandas Series and DataFrames. ``specdal`` also provides
   classes that wrap around Pandas objects for convenience to users
   not familiar with Pandas.

   Users at this level are encouraged to check out the :doc:`data model <data_model>`,
   `Notebook examples
   <https://github.com/EnSpec/SpecDAL/tree/master/specdal/examples/>`_
   , and the :doc:`API <api>`.

2. Command line interface

   Alternatively, users can utilize the command line scripts that
   ``specdal`` provides. The following scripts are currently
   distributed:

   - :doc:`specdal_info <specdal_info>`: displays key information in a spectral file


   - :doc:`specdal_pipeline <specdal_pipeline>`: converts a directory of spectral files into
     .csv files and figures

3. Graphical User Interface (GUI)

   At the highest level, ``SpecDAL`` provides a GUI that requires no
   programming. GUI can be handy for tasks such as outlier detection.
   GUI is provided as an executable, ``specdal_gui`` on Linux/Mac and
   ``specdal_gui.exe`` on Windows.


Examples
========

Check out the example Notebooks `here
<https://github.com/EnSpec/SpecDAL/tree/master/specdal/examples/>`_.
