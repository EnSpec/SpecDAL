=============
API Reference
=============

This is the class and function reference page of SpecDAL.

Spectrum
========

.. automodule:: specdal.containers.spectrum
   :members:

Collection
==========

.. autoclass:: specdal.containers.collection.Collection
   :members: 

.. autofunction:: specdal.containers.collection.df_to_collection

Operators
=========

Specdal's operators perform on both pandas and specdal objects. In the
following operations, pandas series and dataframes correspond to
specdal's spectrum and collection, respectively.

.. automodule:: specdal.operators
   :members:


Readers
=======

Specdal's readers parse a variety of input formats into the common
specdal.containers.spectrum.Spectrum data type. Readers are used 
internally py Specturm and Collection when constructed with the
filename argument, but can also be used individually.

.. autofunction:: specdal.readers.read

.. autofunction:: specdal.readers.asd.read_asd

.. autofunction:: specdal.readers.sig.read_sig

.. autofunction:: specdal.readers.sed.read_sed

.. autofunction:: specdal.readers.pico.read_pico

Filters
=======

Specdal's filters operate on Collection objects, splitting
them into "good" and "bad" spectra based on certain criteria.

.. automodule:: specdal.filters
   :members:

GUI
===

Specdal provides a Tkinter-based GUI for plotting and manually
flagging spectra from Collections.

.. automodule:: specdal.gui.viewer
   :members:
