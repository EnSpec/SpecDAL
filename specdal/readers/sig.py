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
        elif raw_metadata['units'] == "Irradiance, Irradiance":
            colnames = ["wavelength", "ref_irradiance",
                        "tgt_irradiance", "pct_reflect"]
        data = pd.read_csv(filepath, skiprows=i+1,
                             sep="\s+", index_col=0,
                             header=None, names=colnames
        )
        if "pct_reflect" in data:
            data["pct_reflect"] = data["pct_reflect"]/100
    if read_metadata:
        metadata = OrderedDict()
        metadata['file_path'] = f.name
        metadata['file_name'] = f.name.split('\\')[-1][:-4]
        metadata['instrument_type'] = raw_metadata['instrument']
        ################################################################################
        # Integration time
        metadata['integration_time_ref'] = raw_metadata['integration'].split(', ')[0:3]
        metadata['integration_time_tgt'] = raw_metadata['integration'].split(', ')[3:]
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

        #Extract wavelength min/max ranges
        metadata['wavelength_min'] = None
        metadata['wavelength_max'] = None
        if read_data:
            metadata['wavelength_min'] = float(data.index.min())
            metadata['wavelength_max'] = float(data.index.max())

        #Extract scan methods
        try:
            metadata['scan_method_ref'] = raw_metadata['scan method'].split(', ')[0]
            metadata['scan_method_tgt'] = raw_metadata['scan method'].split(', ')[1]
        except:
            metadata['scan_method_ref'] = None
            metadata['scan_method_tgt'] = None

        # Extract scan coadds
        try:
            metadata['scan_coadds_ref'] = raw_metadata['scan coadds'].split(', ')[0:3]
            metadata['scan_coadds_tgt'] = raw_metadata['scan coadds'].split(', ')[3:]
        except:
            metadata['scan_coadds_ref'] = None
            metadata['scan_coadds_tgt'] = None

        # Extract scan time
        try:
            metadata['scan_time_ref'] = raw_metadata['scan time'].split(', ')[0]
            metadata['scan_time_tgt'] = raw_metadata['scan time'].split(', ')[1]
        except:
            metadata['scan_time_ref'] = None
            metadata['scan_time_tgt'] = None

        # Extract scan settings
        try:
            metadata['scan_settings_ref'] = raw_metadata['scan settings'].split(', ')[0]
            metadata['scan_settings_tgt'] = raw_metadata['scan settings'].split(', ')[1]
        except:
            metadata['scan_settings_ref'] = None
            metadata['scan_settings_tgt'] = None

        # Extract external data set 1
        try:
            metadata['external_data_set1_ref'] = raw_metadata['external data set1'].split(', ')[0:16]
            metadata['external_data_set1_tgt'] = raw_metadata['external data set1'].split(', ')[16:]
        except:
            metadata['external_data_set1_ref'] = None
            metadata['external_data_set1_tgt'] = None

        # Extract external data set 2
        try:
            metadata['external_data_set2_ref'] = raw_metadata['external data set2'].split(', ')[0:16]
            metadata['external_data_set2_tgt'] = raw_metadata['external data set2'].split(', ')[16:]
        except:
            metadata['external_data_set2_ref'] = None
            metadata['external_data_set2_tgt'] = None

        # Extract external data-dark and data-mask
        try:
            metadata['external_data_dark'] = raw_metadata['external data dark']
            metadata['external_data_mask'] = raw_metadata['external data mask']
        except:
            metadata['external_data_dark'] = None
            metadata['external_data_mask'] = None

        # Extract optics
        try:
            metadata['optic_ref'] = raw_metadata['optic'].split(', ')[0]
            metadata['optic_tgt'] = raw_metadata['optic'].split(', ')[1]
        except:
            metadata['optic_ref'] = None
            metadata['optic_tgt'] = None

        # Extract temperature
        try:
            metadata['temp_ref'] = raw_metadata['temp'].split(', ')[0:3]
            metadata['temp_tgt'] = raw_metadata['temp'].split(', ')[3:]
        except:
            metadata['temp_ref'] = None
            metadata['temp_tgt'] = None

        # Extract battery
        try:
            metadata['battery_ref'] = raw_metadata['battery'].split(', ')[0]
            metadata['baterry_tgt'] = raw_metadata['battery'].split(', ')[1]
        except:
            metadata['battery_ref'] = None
            metadata['baterry_tgt'] = None

        # Extract time
        try:
            metadata['time_ref'] = raw_metadata['time'].split(', ')[0]
            metadata['time_tgt'] = raw_metadata['time'].split(', ')[1]
        except:
            metadata['time_ref'] = None
            metadata['time_tgt'] = None

        # Extract units
        try:
            metadata['units_ref'] = raw_metadata['units'].split(', ')[0]
            metadata['units_tgt'] = raw_metadata['units'].split(', ')[1]
        except:
            metadata['units_ref'] = None
            metadata['units_tgt'] = None

        # Extract comm
        try:
            metadata['comm'] = raw_metadata['comm']
        except:
            metadata['comm'] = None

        # Extract memory slots
        try:
            metadata['memory_slot_ref'] = raw_metadata['memory slot'].split(', ')[0]
            metadata['memory_slot_tgt'] = raw_metadata['memory slot'].split(', ')[1]
        except:
            metadata['memory_slot_ref'] = None
            metadata['memory_slot_tgt'] = None

        # Extract factors
        try:
            metadata['factors'] = raw_metadata['factors']
        except:
            metadata['factors'] = None

        # Extract inclinometer (ref and target)
        try:
            metadata['inclinometer_x_ref'] = raw_metadata['inclinometer x offset'].split(', ')[0]
            metadata['inclinometer_x_tgt'] = raw_metadata['inclinometer x offset'].split(', ')[1]
            metadata['inclinometer_y_ref'] = raw_metadata['inclinometer y offset'].split(', ')[0]
            metadata['inclinometer_y_tgt'] = raw_metadata['inclinometer y offset'].split(', ')[1]
        except:
            metadata['inclinometer_x_ref'] = None
            metadata['inclinometer_x_tgt'] = None
            metadata['inclinometer_y_ref'] = None
            metadata['inclinometer_y_tgt'] = None

        # Extract sun zenith, amimuth and weather
        try:
            metadata['sun_zenith_ref'] = raw_metadata['sun zenith'].split(', ')[0]
            metadata['sun_zenith_tgt'] = raw_metadata['sun zenith'].split(', ')[1]
            metadata['sun_azimuth_ref'] = raw_metadata['sun azimuth'].split(', ')[0]
            metadata['sun_azimuth_tgt'] = raw_metadata['sun azimuth'].split(', ')[1]
            metadata['weather'] = raw_metadata['weather']

        except:
            metadata['sun_zenith_ref'] = None
            metadata['sun_zenith_tgt'] = None
            metadata['sun_azimuth_ref'] = None
            metadata['sun_azimuth_tgt'] = None
            metadata['weather'] = None

        """
        print(raw_metadata.keys())
        print('\n')
        print(metadata.keys())
        print('\n')
        print("columnas: ", data.columns)
        print(data)
        """

    return data, metadata











