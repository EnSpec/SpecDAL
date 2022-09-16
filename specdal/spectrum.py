# spectrum.py provides class for representing a single
# spectrum. Spectrum class is essentially a wrapper around
# pandas.Series.
import pandas as pd
import numpy as np
import xarray
import specdal.operator as op
from collections import OrderedDict
from .reader import read
from .utils.misc import get_pct_reflect
import os
from numbers import Number
import numpy.lib.mixins
from scipy.integrate import simps

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
                 verbose=False, reader=None):
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
            self.read(filepath, measure_type, verbose=verbose, reader=reader)
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
    def read(self, filepath, measure_type, verbose=False, reader=None):
        '''
        Read measurement from a file.
        '''
        data, meta = read(filepath, verbose=verbose, reader=reader)
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

    def savgol_filter(self, window_length, polyorder, deriv=0,
                        delta=1.0, axis=-1, mode='interp', cval=0.0):
        '''
        '''
        self.measurement = op.savgol(self.measurement, 
                        window_length, polyorder, deriv,
                        delta, axis, mode, cval)
        self.savgol_window = window_length
        self.savgol_polyorder = polyorder
        
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

    ##################################################
    # wrapper for spectral subset
    def walevength_range(self, wlmin=350, wlmax=2500, dtype=None):
        self.measurement = self.measurement.loc[wlmin:wlmax]
        self.metadata['wavelength_range'] = (wlmin, wlmax)


    ##################################################
    # wrapper for array operations
    def __array__(self, dtype=None):
        return self.measurement.values

    ##################################################
    # method for computing the values for a specific satellite

    def getRSR(self, satellite="aqua", sensor="modis", rsr_path=__file__.replace("/spectrum.py","/rsr/")):
        # We build a list of available rsr
        available_rsr = [x[:-7] for x in os.listdir(rsr_path) if x[0] != "."]
        # Build rsr
        if sensor == "aviris":
            rsr_path = rsr_path+f"{sensor}_RSR.nc"
        else:
            rsr_path = rsr_path+f"{satellite}_{sensor}_RSR.nc"
        # Read bands from dataframe
        try:
            df = xarray.open_dataset(rsr_path).to_dataframe()
        except (FileNotFoundError, IOError):
            print(f"Satellite-sensor combination not available. The options are {available_rsr}")

        # Reshape the dataframe as needed
        df.reset_index(inplace=True)
        df.drop(["wavelengths"], axis=1, inplace=True)
        #df.set_index(["bands","wavelength"], inplace=True)
        rsr = df.pivot(index="wavelength", columns="bands")
        rsr.columns = rsr.columns.droplevel()
        rsr.columns.name=None
        rsr.index.name = "Wavelength"
        # round index to 1 decimal
        rsr.index = rsr.index.values.round(0)
        # We sort the dataframe
        rsr = rsr[sorted(rsr.columns)]
        # Remove duplicated indices and sort by index
        rsr = rsr.groupby(level=0).sum().sort_index()
        
        return rsr

    def getSatellite(self, satellite="aqua", sensor="modis", rsr_path = __file__.replace("/spectrum.py","/rsr/")):
        # get relative spectral response
        rsr = self.getRSR(satellite, sensor, rsr_path)
        # compute reflectance by band
        ref = rsr.mul(self.measurement, axis='index').sum(axis="index")/rsr.sum(axis="index")
        # save to spectrum
        name = self.name
        spectrum = Spectrum(name=name, measurement=ref, metadata=self.metadata, measure_type=self.measure_type)

        spectrum.metadata["satellite"] = satellite
        spectrum.metadata["sensor"] = sensor
        
        return spectrum



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
    
