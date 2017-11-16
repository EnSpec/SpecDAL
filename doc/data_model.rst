==========
Data Model
==========

SpecDAL relies on Pandas data structures to represent spectroscopy
measurements. A single measurement is stored in pandas.Series while a
collection of measurements is stored in pandas.DataFrame. SpecDAL
provides Spectrum and Collection classes that wraps Series and
DataFrames along with spectral metadata. Spectral operators, such as
interpolation, are provided as functions on pandas objects or as
methods of specdal's classes.


Pandas Representation of Spectra
================================

Series - single spectrum
------------------------

DataFrame - collection of spectra
---------------------------------



Spectrum and Collection Classes
===============================

Spectrum - single spectrum
--------------------------

Collection - collection of spectra
----------------------------------


Operators
=========

