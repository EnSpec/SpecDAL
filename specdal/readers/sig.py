# readers.py provides functions to read .sig spectrum files for data and
# metadata.

import pandas as pd
import numpy as np
from os.path import abspath, expanduser, splitext, basename, join, split
import glob
from collections import OrderedDict
import json

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
        data = pd.read_csv(filepath, skiprows=i+1,
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
        try:
            metadata['gps_time_ref'], metadata['gps_time_tgt'] = tuple(
                map(float, raw_metadata['gpstime'].replace(' ', '').split(',')))
        except:
            metadata['gps_time_tgt'] = None
            metadata['gps_time_ref'] = None

        metadata['wavelength_range'] = None
        if read_data:
            metadata['wavelength_range'] = (data.index.min(), data.index.max())
    return data, metadata
