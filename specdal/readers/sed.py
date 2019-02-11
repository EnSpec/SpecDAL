# readers.py provides functions to read .sed spectrum files for data and
# metadata.

import pandas as pd
import numpy as np
from os.path import abspath, expanduser, splitext, basename, join, split
import glob
from collections import OrderedDict
import json

SED_COLUMNS = {
    "Wvl": "wavelength",
    "Rad. (Target)": "tgt_reflect",
    'Rad. (Ref.)': "ref_reflect",
    "Tgt./Ref. %": "pct_reflect",
    "Irrad. (Ref.)": "ref_irradiance",
    "Irrad. (Target)": "tgt_irradiance",
    "Norm. DN (Ref.)": "ref_count",
    "Norm. DN (Target)": "tgt_count",
    "Reflect. %": "pct_reflect",
    "Reflect. [1.0]":"dec_reflect",
    "Chan.#":"channel_num",
}

def read_sed(filepath, read_data=True, read_metadata=True, verbose=False):
    """
    Read sed file for data and metadata
    
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
        data = pd.read_csv(filepath, skiprows=i+1,
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
