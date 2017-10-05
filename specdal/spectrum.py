# spectrum.py provides class for representing a single
# spectrum. Spectrum class is essentially a wrapper around
# pandas.Series.
import pandas as pd
import numpy as np
import specdal.operator as op
from collections import OrderedDict
from .reader import read
from .utils.misc import get_pct_reflect
import os

class Spectrum(object):
    """Class that represents a single spectrum
    
    Parameters
    ----------
    
    name: string
        Name of the spectrum. 
    
    filepath: string (optional)
        Path to the file to read from.
    
    measurement: pandas.Series
        Spectral measurement
    
    metadata: OrderedDict
        Metadata associated with spectrum
    
    Notes
    -----
    
    Spectrum object stores a single spectral measurement using
    pandas.Series with index named: "wavelength".
    
    """
    def __init__(self, name=None, filepath=None, measurement=None,
                 measure_type='pct_reflect', metadata=None,
                 resampled=False, stitched=False, jump_corrected=False,
                 verbose=False):
        if name is None:
            assert filepath is not None
            name = os.path.splitext(os.path.basename(filepath))[0]
        self.name = name
        self.measurement = measurement
        self.measure_type = measure_type
        self.metadata = metadata
        self.resampled = resampled
        self.stitched = stitched
        self.jump_corrected = jump_corrected
        if filepath:
            self.read(filepath, measure_type, verbose=verbose)
    def __str__(self):
        string = "\nname:\t\t{!s},\n".format(self.name)
        string += "measure_type:\t{!s}\n".format(self.measure_type)
        string += "measurements:\twave  |measurement\n"
        string += "\t\t------|-----------\n"
        string += "\t\t {0:.1f}|{1:.3f}\n".format(
            self.measurement.head(1).index.values[0],
            self.measurement.head(1).values[0])
        string += "\t\t   ...|...\n"
        string += "\t\t{0:.1f}|{1:.3f}\n".format(self.measurement.tail(1).index.values[0],
                                        self.measurement.tail(1).values[0])
        string += "metadata:"
        for i, (key, item) in enumerate(self.metadata.items()):
            if i > 0:
                string += "\t"
            string += "\t{}:{}\n".format(key, item)
        return string
    ##################################################
    # reader
    def read(self, filepath, measure_type, verbose=False):
        '''
        Read measurement from a file.
        '''
        data, meta = read(filepath, verbose=verbose)
        self.metadata = meta
        if measure_type == 'pct_reflect' and 'pct_reflect' not in data:
            self.measurement = get_pct_reflect(data)
            return
        assert measure_type in data # TODO: handle this
        self.measurement = data[measure_type]
    ##################################################
    # wrappers around spectral operations
    def resample(self, spacing=1, method='slinear'):
        '''
        '''
        self.measurement = op.resample(self.measurement, spacing, method)
        self.resampled = True
    def stitch(self, method='mean'):
        '''
        '''
        self.measurement = op.stitch(self.measurement, method)
        self.stitched = True
    def jump_correct(self, splices, reference, method="additive"):
        '''
        '''
        self.measurement = op.jump_correct(self.measurement, splices, reference, method)
        self.jump_corrected = True
    ##################################################
    # wrapper around plot function
    def plot(self, *args, **kwargs):
        ''''''
        return self.measurement.plot(*args, **kwargs)
    def to_csv(self, *args, **kwargs):
        ''''''
        return pd.DataFrame(self.measurement).transpose().to_csv(
            *args, **kwargs)
    ##################################################
    # wrapper around pandas series operators
    def __add__(self, other):
        new_measurement = None
        new_name = self.name + '+'
        if isinstance(other, Spectrum):
            assert self.measure_type == other.measure_type
            new_measurement = self.measurement.__add__(other.measurement).dropna()
            new_name += other.name
        else:
            new_measurement = self.measurement.__add__(other)
        return Spectrum(name=new_name, measurement=new_measurement,
                        measure_type=self.measure_type)
    def __isub__(self, other):
        pass
    def __imul__(self, other):
        pass
    def __itruediv__(self, other):
        pass
    def __ifloordiv__(self, other):
        pass
    def __iiadd__(self, other):
        pass
    def __isub__(self, other):
        pass
    def __imul__(self, other):
        pass
    def __itruediv__(self, other):
        pass
    def __ifloordiv__(self, other):
        pass
    
