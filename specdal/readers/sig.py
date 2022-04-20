# readers.py provides functions to read .sig spectrum files for data and
# metadata.

import pandas as pd
import numpy as np
from os.path import abspath, expanduser, splitext, basename, join, split
import glob
from collections import OrderedDict
import json

#Convert to degrees and minutes with sign
def extract_longitude(longitude):
    """
    Input: string
    Output: float
    """
    degrees = float(longitude[0:3])
    minutes = float(longitude[3:-1])/60.0
    sign_string = longitude[-1]
    if sign_string == 'W':
        sign = int(-1)
    else:
        sign = int(1)
    longitude_global = (degrees + minutes)*sign
    return longitude_global

def extract_latitude(latitude):
    """
    Input: string
    Output: float
    """
    degrees = float(latitude[0:2])
    minutes = float(latitude[2:-1])/60.0
    sign_string = latitude[-1]
    if sign_string == 'S':
        sign = int(-1)
    else:
        sign = int(1)
    latitude_global = (degrees + minutes)*sign
    return latitude_global


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
        metadata['instrument_type'] = raw_metadata['instrument']
        #metadata['instrument_type'] = 'SIG'
        ################################################################################
        # Average the integration times
        # TODO: check if this is valid
        metadata['integration_time'] =  np.mean( 
            list(map(float, raw_metadata['integration'].split(', '))))
        ################################################################################
        metadata['measurement_type'] = raw_metadata['units'].split(', ')[0]
        # Extract GpsTime
        try:
            metadata['gps_time_ref'], metadata['gps_time_tgt'] = tuple(
                map(float, raw_metadata['gpstime'].replace(' ', '').split(',')))
        except:
            metadata['gps_time_tgt'] = None
            metadata['gps_time_ref'] = None
        # Extract longitude
        try:
            metadata['longitude_ref'], metadata['longitude_tgt'] = tuple(
                map(str, raw_metadata['longitude'].replace(' ', '').split(',')))
            #Convert longitude string to float (reference and target)
            metadata['longitude_ref'] = extract_longitude(metadata['longitude_ref'])
            metadata['longitude_tgt'] = extract_longitude(metadata['longitude_tgt'])
        except:
            metadata['longitude_ref'] = None
            metadata['longitude_tgt'] = None
        # Extract latitude
        try:
            metadata['latitude_ref'], metadata['latitude_tgt'] = tuple(
                map(str, raw_metadata['latitude'].replace(' ', '').split(',')))
            #Convert latitude string to float (reference and target)
            metadata['latitude_ref'] = extract_latitude(metadata['latitude_ref'])
            metadata['latitude_tgt'] = extract_latitude(metadata['latitude_tgt'])
        except:
            metadata['latitude_ref'] = None
            metadata['latitude_tgt'] = None

        # Extract error at reference or target
        try:
            metadata['error_ref'] = raw_metadata['error'][0]
            metadata['error_tgt'] = raw_metadata['error'][-1]
        except:
            metadata['error_ref'] = None
            metadata['error_tgt'] = None

        #metadata['wavelength_range'] = None
        metadata['wavelength_min'] = None
        metadata['wavelength_max'] = None
        if read_data:
            #metadata['wavelength_range'] = (data.index.min(), data.index.max())
            metadata['wavelength_min'] = float(data.index.min())
            metadata['wavelength_max'] = float(data.index.max())

    return data, metadata
