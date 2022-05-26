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
from numbers import Number
import numpy.lib.mixins

class Spectrum(numpy.lib.mixins.NDArrayOperatorsMixin):
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
                 interpolated=False, stitched=False, jump_corrected=False,
                 vector_normalized=False, derivative_order=0,
                 verbose=False):
        if name is None:
            assert filepath is not None
            name = os.path.splitext(os.path.basename(filepath))[0]
        self.name = name
        self.measurement = measurement
        self.measure_type = measure_type
        self.metadata = metadata
        self.interpolated = interpolated
        self.stitched = stitched
        self.jump_corrected = jump_corrected
        self.vector_normalized = vector_normalized
        self.derivative_order = derivative_order
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
    def interpolate(self, spacing=1, method='slinear'):
        '''
        '''
        self.measurement = op.interpolate(self.measurement, spacing, method)
        self.interpolated = True
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
    def vector_normalize(self):
        '''
        '''
        self.measurement = op.vector_normalize(self.measurement)
        self.vector_normalized = True
    def derivative(self):
        '''
        '''
        self.measurement = op.derivative(self.measurement)
        self.derivative_order += 1
        
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
    # wrapper for numpy functions
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        new_measurement = None
        new_name = self.name + '+'
        if method == '__call__':
            if self.metadata is None:
                metadata = None
            else:
                metadata = self.metadata
                metadata['file'] = None
                metadata["measurement_type"]="TRANS_TYPE"
            new_name = ufunc.__name__+"("
            values = []
            for input in inputs:
                if isinstance(input, Number):
                    values.append(input)
                    new_name = new_name +str(input)+", "
                elif isinstance(input, Spectrum):
                    values.append(input.measurement)
                    new_name = new_name+input.name+", "
                else:
                    return NotImplemented
            
            new_name = new_name[:-2]+")"
            if metadata is not None:
                metadata['name'] = new_name
            return Spectrum(name=new_name, measurement=ufunc(*values, **kwargs),metadata=metadata, measure_type = 'TRANS_TYPE')
        else:
            return NotImplemented
    
    # wrapper for array operations
    def __array__(self, dtype=None):
        return self.measurement.values

    # wrapper around pandas series operators
    # def __add__(self, other):
    #     new_measurement = None
    #     new_name = self.name + '+'
    #     if isinstance(other, Spectrum):
    #         assert self.measure_type == other.measure_type
    #         new_measurement = self.measurement.__add__(other.measurement).dropna()
    #         new_name += other.name
    #     else:
    #         new_measurement = self.measurement.__add__(other)
    #     return Spectrum(name=new_name, measurement=new_measurement,
    #                     measure_type=self.measure_type)
    # def __isub__(self, other):
    #     pass
    # def __imul__(self, other):
    #     pass
    # def __itruediv__(self, other):
    #     pass
    # def __ifloordiv__(self, other):
    #     pass
    # def __iiadd__(self, other):
    #     pass
    # def __isub__(self, other):
    #     pass
    # def __imul__(self, other):
    #     pass
    # def __itruediv__(self, other):
    #     pass
    # def __ifloordiv__(self, other):
    #     pass
    
