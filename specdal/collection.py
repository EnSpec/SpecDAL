# collection.py provides class for representing multiple
# spectra. Collection class is essentially a wrapper around
# pandas.DataFrame.
import pandas as pd
import numpy as np
from collections import OrderedDict, defaultdict
from .spectrum import Spectrum
import specdal.operator as op
from itertools import groupby
from .reader import read
import copy
import warnings
from os.path import abspath, expanduser, splitext
import os

################################################################################
# key functions for forming groups
def separator_keyfun(spectrum, separator, indices):
    elements = spectrum.name.split(separator)
    return separator.join([elements[i] for i in indices])

def separator_with_filler_keyfun(spectrum, separator, indices, filler='.'):
    elements = spectrum.name.split(separator)
    return separator.join([elements[i] if i in indices else
                           fill for i in range(len(elements))])

def df_to_collection(df, name, measure_type='pct_reflect'):
    '''
    Create a collection from a pandas.DataFrame
    
    Parameters
    ----------

    df: pandas.DataFrame
        Must have spectrum.name as index and metadata or wavelengths as columns
    
    name: string
        Name to assign to collection
    
    Returns
    -------
    c: specdal.Collection object
    
    '''
    c = Collection(name=name, measure_type=measure_type)
    wave_cols, meta_cols = op.get_column_types(df)
    metadata_dict = defaultdict(lambda: None)
    if len(meta_cols) > 0:
        metadata_dict = df[meta_cols].transpose().to_dict()
    measurement_dict = df[wave_cols].transpose().to_dict('series')
    for spectrum_name in df.index:
        c.append(Spectrum(name=spectrum_name,
                          measurement=measurement_dict[spectrum_name],
                          measure_type=measure_type,
                          metadata=metadata_dict[spectrum_name]))
    return c

def proximal_join(base, rover, on='gps_time_tgt', direction='nearest'):
    '''
    Perform proximal join and return a new collection.

    Parameters
    ----------
    
    base: DataFrame or specdal.Collection object
    
    rover: DataFrame or specdal.Collection object

    Returns
    -------
    result: proximally joined dataset
        default: specdal.Collection object
        if output_df is True: pandas.DataFrame object
    '''
    result = None
    return_collection = False
    name = 'proximally_joined'
    if isinstance(base, Collection):
        return_collection = True
        base = base.data_with_meta(fields=[on])
    if isinstance(rover, Collection):
        return_collection = True
        name = rover.name
        rover = rover.data_with_meta(fields=[on])
    result = op.proximal_join(base, rover, on=on, direction=direction)
    if return_collection:
        result = df_to_collection(result, name=name)
    return result

################################################################################
# main Collection class
class Collection(object):
    """
    Represents a dataset consisting of a collection of spectra
    """
    def __init__(self, name, directory=None, spectra=None,
                 measure_type='pct_reflect', metadata=None, masks=None):
        self.name = name
        self.spectra = spectra
        self.measure_type = measure_type
        self.metadata = metadata
        self.masks = masks
        if directory:
            self.read(directory, measure_type)
    @property
    def spectra(self):
        """
        A list of Spectrum objects in the collection
        """
        return list(self._spectra.values())
    @spectra.setter
    def spectra(self, value):
        self._spectra = OrderedDict()
        if value is not None:
            # assume value is an iterable such as list
            for spectrum in value:
                assert spectrum.name not in self._spectra
                self._spectra[spectrum.name] = spectrum
    @property
    def masks(self):
        """
        A dict of masks for each spectrum in the collection
        """
        return self._masks
    @masks.setter
    def masks(self, value):
        '''
        TODO: test this
        '''
        self._masks = defaultdict(lambda: False)
        if value is not None:
            for v in value:
                if v in self._spectra:
                    self._masks[v] = True
    def mask(self, spectrum_name):
        self.masks[spectrum_name] = True
    def unmask(self, spectrum_name):
        del self.masks[spectrum_name]
        
    @property
    def data(self):
        '''
        Get measurements as a Pandas.DataFrame
        '''
        try:
            return pd.concat(objs=[s.measurement for s in self.spectra],
                             axis=1, keys=[s.name for s in self.spectra])
        except ValueError as err:
            # typically from duplicate index due to overlapping wavelengths
            if not all([s.stitched for s in self.spectra]):
                warnings.warn('ValueError: Try after stitching the overlaps')
            raise err
    def append(self, spectrum):
        """
        insert spectrum to the collection
        """
        assert spectrum.name not in self._spectra
        assert isinstance(spectrum, Spectrum)
        self._spectra[spectrum.name] = spectrum
        
    def data_with_meta(self, data=True, fields=None):
        """
        Get dataframe with additional columns for metadata fields
        
        Parameters
        ----------
        
        data: boolean
            whether to return the measurement data or not
        
        fields: list
            names of metadata fields to include as columns.
            If None, all the metadata will be included.
        
        Returns
        -------
        pd.DataFrame: self.data with additional columns
        
        """
        if fields is None:
            fields = ['file', 'instrument_type', 'integration_time',
                      'measurement_type', 'gps_time_tgt', 'gps_time_ref',
                      'wavelength_range']
        meta_dict = {}
        for field in fields:
            meta_dict[field] = [s.metadata[field] if field in s.metadata
                                else None for s in self.spectra]
        meta_df = pd.DataFrame(meta_dict, index=[s.name for s in self.spectra])
        if data:
            result = pd.merge(meta_df, self.data.transpose(),
                              left_index=True, right_index=True)
        else:
            result = meta_df
        return result

    ##################################################
    # object methods
    def __getitem__(self, key):
        return self._spectra[key]
    def __delitem__(self, key):
        self._spectra.__delitem__(key)
        self._masks.__delitem__(key)
    def __missing__(self, key):
        pass
    def __len__(self):
        return len(self._spectra)
    def __contains__(self, item):
        self._spectra.__contains__(item)
    ##################################################
    # reader
    def read(self, directory, measure_type='pct_reflect',
             ext=[".asd", ".sed", ".sig"], recursive=False,
             verbose=False):
        """
        read all files in a path matching extension
        """
        directory = abspath(expanduser(directory))
        for dirpath, dirnames, filenames in os.walk(directory):
            if not recursive:
                # only read given path
                if dirpath != directory:
                    continue
            for f in sorted(filenames):
                f_name, f_ext = splitext(f)
                if f_ext not in list(ext):
                    # skip to next file
                    continue
                filepath = os.path.join(dirpath, f)
                spectrum = Spectrum(name=f_name, filepath=filepath,
                                    measure_type=measure_type,
                                    verbose=verbose)
                self.append(spectrum)
    ##################################################
    # wrapper around spectral operations
    def resample(self, spacing=1, method='slinear'):
        '''
	'''
        for spectrum in self.spectra:
            spectrum.resample(spacing, method)
    def stitch(self, method='mean'):
        '''
	'''
        for spectrum in self.spectra:
            spectrum.stitch(method)
    def jump_correct(self, splices, reference, method='additive'):
        '''
	'''
        for spectrum in self.spectra:
            spectrum.jump_correct(splices, reference, method)
    ##################################################
    # group operations
    def groupby(self, separator, indices, filler=None):
        """
        Group the spectra using a separator pattern
        
        Returns
        -------
        OrderedDict consisting of specdal.Collection objects for each group
            key: group name
            value: collection object
        
        """
        args = [separator, indices]
        key_fun = separator_keyfun
        if filler is not None:
            args.append(filler)
            key_fun = separator_with_filler_keyfun
        spectra_sorted = sorted(self.spectra,
                                  key=lambda x: key_fun(x, *args))
        groups = groupby(spectra_sorted,
                         lambda x: key_fun(x, *args))
        result = OrderedDict()
        for g_name, g_spectra in groups:
            coll = Collection(name=g_name,
                              spectra=[copy.deepcopy(s) for s in g_spectra])
            result[coll.name] = coll
        return result
    def plot(self, *args, **kwargs):
        '''
        '''
        self.data.plot(*args, **kwargs)
        pass
    def to_csv(self, *args, **kwargs):
        '''
        '''
        self.data.transpose().to_csv(*args, **kwargs)
    ##################################################
    # aggregate
    def mean(self, append=False):
        '''
        '''
        spectrum = Spectrum(name=self.name + '_mean',
                            measurement=self.data.mean(axis=1),
                            measure_type=self.measure_type)
        if append:
            self.append(spectrum)
        return spectrum
    def median(self, append=False):
        '''
	'''
        spectrum = Spectrum(name=self.name + '_median',
                            measurement=self.data.median(axis=1),
                            measure_type=self.measure_type)
        if append:
            self.append(spectrum)
        return spectrum
    def min(self, append=False):
        '''
	'''
        spectrum = Spectrum(name=self.name + '_min',
                            measurement=self.data.min(axis=1),
                            measure_type=self.measure_type)
        if append:
            self.append(spectrum)
        return spectrum
    def max(self, append=False):
        '''
	'''
        spectrum = Spectrum(name=self.name + '_max',
                            measurement=self.data.max(axis=1),
                            measure_type=self.measure_type)
        if append:
            self.append(spectrum)
        return spectrum
    def std(self, append=False):
        '''
	'''
        spectrum = Spectrum(name=self.name + '_std',
                            measurement=self.data.std(axis=1),
                            measure_type=self.measure_type)
        if append:
            self.append(spectrum)
        return spectrum

