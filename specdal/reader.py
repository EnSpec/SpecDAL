# readers.py provides functions to read spectrum files for data and
# metadata.

import pandas as pd
import numpy as np
from os.path import abspath, expanduser, splitext
from collections import OrderedDict
from .utils.reader_utils import *

def read(filepath, read_data=True, read_metadata=True, verbose=False):
    """
    Calls the appropriate reader based on file extension
    """
    SUPPORTED_READERS = {'.asd':read_asd , '.sig':read_sig , '.sed':read_sed }
    ext = splitext(filepath)[1]
    assert ext in SUPPORTED_READERS
    reader = SUPPORTED_READERS[ext]
    return reader(abspath(expanduser(filepath)), read_data,
                  read_metadata, verbose)

def read_sed(filepath, read_data=True, read_metadata=True, verbose=False):
    """
    Read asd file for data and metadata
    
    Return
    ------
    2-tuple of (pd.DataFrame, OrderedDict) for data, metadata
    """
    data = None
    metadata = None
    raw_metadata = {}
    # first, get raw metadata and line number of data
    with open(abspath(expanduser(filepath)), 'r') as f:
        if verbose:
            print('reading {}'.format(filepath))
        for i, line in enumerate(f):
            if line[0:5] == 'Data:':
                break
            field = line.strip().split(': ')
            if len(field) > 1:
                raw_metadata[field[0]] = field[1]
    if read_data:
        data = pd.read_table(filepath, skiprows=i+1,
                             sep='\t')
        data.columns = [SED_COLUMNS[col] for col in data.columns]
        data = data.set_index("wavelength")
        if "pct_reflect" in data:
            data["pct_reflect"] = data["pct_reflect"]/100
        if "dec_reflect" in data:
            data["pct_reflect"] = data["dec_reflect"]
    if read_metadata:
        metadata = OrderedDict()
        metadata['file'] = f.name
        metadata['instrument_type'] = 'SED'
        ################################################################################
        # Average the integration times
        # TODO: check if this is valid
        metadata['integration_time'] =  np.mean( 
            list(map(int, raw_metadata['Integration'].split(','))))
        ################################################################################
        metadata['measurement_type'] = raw_metadata['Measurement']
        metadata['gps_time_tgt'] = None
        metadata['gps_time_ref'] = None
        if raw_metadata['GPS Time'] != 'n/a':
            # TODO: WILL THIS BE A TUPLE?
            metadata['gps_time_tgt'] = raw_metadata['GPS Time']
        metadata['wavelength_range'] = tuple(map(int, raw_metadata['Wavelength Range'].split(',')))
    return data, metadata

def read_sig(filepath, read_data=True, read_metadata=True, verbose=False):
    """
    Read asd file for data and metadata
    
    Return
    ------
    2-tuple of (pd.DataFrame, OrderedDict) for data, metadata
    """
    data = None
    metadata = None
    raw_metadata = {}
    # first, get raw metadata and line number of data
    with open(abspath(expanduser(filepath)), 'r') as f:
        if verbose:
            print('reading {}'.format(filepath))
        for i, line in enumerate(f):
            if line[0:5] == 'data=':
                break
            field = line.strip().split('= ')
            if len(field) > 1:
                raw_metadata[field[0]] = field[1].strip()
    if read_data:
        # read data
        if raw_metadata['units'] == "Counts, Counts":
            colnames = ["wavelength", "ref_counts",
                        "tgt_counts", "pct_reflect"]
        elif raw_metadata['units'] == "Radiance, Radiance":
            colnames = ["wavelength", "ref_radiance",
                        "tgt_radiance", "pct_reflect"]
        data = pd.read_table(filepath, skiprows=i+1,
                             sep="\s+", index_col=0,
                             header=None, names=colnames
        )
        if "pct_reflect" in data:
            data["pct_reflect"] = data["pct_reflect"]/100
    if read_metadata:
        metadata = OrderedDict()
        metadata['file'] = f.name
        metadata['instrument_type'] = 'SIG'
        ################################################################################
        # Average the integration times
        # TODO: check if this is valid
        metadata['integration_time'] =  np.mean( 
            list(map(float, raw_metadata['integration'].split(', '))))
        ################################################################################
        metadata['measurement_type'] = raw_metadata['units'].split(', ')[0]
        metadata['gps_time_tgt'] = None
        metadata['gps_time_ref'] = None
        if raw_metadata['gpstime'] != ',':
            metadata['gps_time_ref'], metadata['gps_time_tgt'] = tuple(
                map(float, raw_metadata['gpstime'].replace(' ', '').split(',')))
        metadata['wavelength_range'] = None
        if read_data:
            metadata['wavelength_range'] = (data.index.min(), data.index.max())
    return data, metadata

def read_asd(filepath, read_data=True, read_metadata=True, verbose=False):
    """
    Read asd file for data and metadata
    
    Return
    ------
    2-tuple of (pd.DataFrame, OrderedDict) for data, metadata
    """
    data = None
    metadata = None
    if read_metadata:
        metadata = OrderedDict()
    with open(abspath(expanduser(filepath)), 'rb') as f:
        if verbose:
            print('reading {}'.format(filepath))
        metadata['file'] = f.name
        metadata['instrument_type'] = 'ASD'
        binconts = f.read()
        version = binconts[0:3].decode('utf-8')
        assert(version in ASD_VERSIONS) # TODO: define ASD_VERSIONS
        # read spectrum type
        spectrum_type_index = struct.unpack('B', binconts[186:(186 + 1)])[0]
        spectrum_type = list(ASD_DATA_TYPES.keys())[spectrum_type_index]
        # read wavelength info
        wavestart = struct.unpack('f', binconts[191:(191 + 4)])[0]
        wavestep = struct.unpack('f', binconts[195:(195 + 4)])[0] # in nm
        num_channels = struct.unpack('h', binconts[204:(204 + 2)])[0]
        wavestop = wavestart + num_channels*wavestep - 1
        if read_data:
            # read data
            tgt_column = ASD_DATA_TYPES[spectrum_type]
            ref_column = tgt_column.replace('tgt', 'ref')
            data_format = struct.unpack('B', binconts[199:(199 + 1)])[0]
            fmt = 'f'*num_channels
            if data_format == 2:
                fmt = 'd'*num_channels
            if data_format == 0:
                fmt = 'f'*num_channels
            # data to DataFrame
            size = num_channels*8
            # Read the spectrum block data
            waves = np.linspace(wavestart, wavestop, num_channels)
            spectrum = np.array(struct.unpack(fmt, binconts[484:(484 + size)]))
            reference = None
            if ASD_HAS_REF[version]:
                # read reference
                start = 484 + size
                ref_flag = struct.unpack('??', binconts[start: start + 2])[0]
                first, last = start + 18, start + 20
                ref_desc_length = struct.unpack('H', binconts[first:last])[0]
                first = start + 20 + ref_desc_length
                last = first + size
                reference = np.array(struct.unpack(fmt, binconts[first:last]))
            data = pd.DataFrame({tgt_column : spectrum,
                                 ref_column: reference}, index=waves)
            data.index.name = 'wavelength'
            data.dropna(axis=1, how='all')
        if read_metadata:
            # read splice wavelength
            splice1 = struct.unpack('f', binconts[444:(444 + 4)])[0]
            splice2 = struct.unpack('f', binconts[448:(448 + 4)])[0]
            # integration time
            integration_time = struct.unpack('= L', binconts[390:(390 + 4)])[0] # in ms
            # gps info
            gps_struct = ASD_GPS_DATA.unpack(binconts[344:(344+56)])
            gps_true_heading, gps_speed, gps_latitude, gps_longitude, gps_altitude = gps_struct[:5]
            gps_flags = gps_struct[5:7] # unpack this into bits
            gps_hardware_mode = gps_struct[7]
            gps_timestamp = gps_struct[8]
            gps_flags2 = gps_struct[9:11] # unpack this into bits
            gps_satellites = gps_struct[11:16]
            gps_filler = gps_struct[16:18]
            # metadata
            metadata['integration_time'] = integration_time
            metadata['measurement_type'] = spectrum_type
            metadata['gps_time_tgt'] = gps_timestamp
            metadata['gps_time_ref'] = None
            metadata['wavelength_range'] = (wavestart, wavestop)
            # metadata['splice'] = (splice1, splice2)
            # metadata['resolution'] = wavestep
    return data, metadata
