# readers.py provides functions to read .asd spectrum files for data and
# metadata.


import pandas as pd
import numpy as np
from os.path import abspath, expanduser, splitext, basename, join, split
import glob
from collections import OrderedDict
import json
import struct

ASD_VERSIONS = ['ASD', 'asd', 'as6', 'as7', 'as8']
ASD_HAS_REF = {'ASD': False, 'asd': False, 'as6': True, 'as7': True,
               'as8': True}
ASD_DATA_TYPES = OrderedDict([("RAW_TYPE", "tgt_count"),
                              ("REF_TYPE", "tgt_reflect"),
                              ("RAD_TYPE", "tgt_radiance"),
                              ("NOUNITS_TYPE", None),
                              ("IRRAD_TYPE", "tgt_irradiance"),
                              ("QI_TYPE", None),
                              ("TRANS_TYPE", None),
                              ("UNKNOWN_TYPE", None),
                              ("ABS_TYPE", None)])
ASD_GPS_DATA = struct.Struct("= 5d 2b cl 2b 5B 2c")

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
    raw_metadata = {}
    with open(abspath(expanduser(filepath)), 'rb') as f:
        if verbose:
            print('reading {}'.format(filepath))
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
            metadata['file'] = f.name
            metadata['instrument_type'] = 'ASD'
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
