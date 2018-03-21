# readers.py provides functions to read spectrum files for data and
# metadata.

import pandas as pd
import numpy as np
from os.path import abspath, expanduser, splitext, basename, join, split
import glob
from collections import OrderedDict
import json

PICO_GPS_KEYS = "gps","GPS start","GPS"

class PiccoloFileError(Exception):
    """Error type for piccolo-related issues"""
    pass

def _find_pico_dark(pico_light_path):
    """
    Recent piccolo versions store dark and light spectra in different locations
    Default naming conventions are a bit tricky (timestamp changes between 
    light and dark), so we need to check every dark file in the directory 
    """
    #easy case - there's just one dark and one light file, so they have 
    #the same time stamp
    first_end = "0000.pico.light"
    if pico_light_path.endswith(first_end):
        return pico_light_path[:-len(first_end)]+"0000.pico.dark"
    #harder case - there's multiple light files per dark, so find the dark
    #with the closest timestamp before this one
    #assume there's not that many dark files
    dark_files = glob.glob(join(split(pico_light_path)[0],"*.dark"))
    #insert our light file in here, its dark file will come immediately before
    #it when sorted
    dark_files.append(pico_light_path)
    dark_files.sort()
    dark_idx = dark_files.index(pico_light_path)-1
    if dark_idx == -1:
        raise PiccoloFileError("Unable to find .pico.dark file for {}"
                .format(pico_light_path))
    #TODO: It's still possible there's not a matching dark file
    #(eg we've chosen the wrong dark file)
    return dark_files[dark_idx]
    
def read_pico(filepath, read_data=True, read_metadata=True, verbose=False):
    """
    Read pico file for data and metadata
    
    Return
    ------
    2-tuple of (pd.DataFrame, OrderedDict) for data, metadata
    """
    data = None
    metadata = None
    raw_metadata = {}
    with open(abspath(expanduser(filepath)), 'r') as f:
        if verbose:
            print('reading {}'.format(filepath))
        raw_metadata = json.load(f)    
    
    #dark spectra are stored in a different file for some piccolo formats
    if filepath.endswith('.pico.light'):
        with open(_find_pico_dark(filepath),'r') as f:
            dark_metadata = json.load(f)
            raw_metadata['Spectra'] += dark_metadata['Spectra']

    #TODO: How to handle multiple spectrometers per file?
    #For now, just return the first one

    spectrometer = raw_metadata["Spectra"][0]["Metadata"]["name"]
    #the 4 spectra we need to get a complete measurement
    downwelling_light = None
    downwelling_dark = None
    upwelling_light = None
    upwelling_dark = None
    #figure out which of the 4 spectra we need
    for spectrum in raw_metadata["Spectra"]:
        meta = spectrum["Metadata"]
        if meta["name"] == spectrometer:
            if meta["Dark"] and meta["Direction"]=="Upwelling":
                upwelling_dark = spectrum
            elif meta["Dark"] and meta["Direction"]=="Downwelling":
                downwelling_dark = spectrum
            elif meta["Direction"] == "Upwelling":
                upwelling_light = spectrum
            elif meta["Direction"] == "Downwelling":
                downwelling_light = spectrum


    if read_data:
        if(downwelling_light is None or downwelling_dark is None or
           upwelling_light is None or upwelling_dark is None):
            raise PiccoloFileError("Piccolo File missing necessary spectrum")
        #Pico always in raw counts
        wavelength_coeffs = downwelling_light["Metadata"][
                "WavelengthCalibrationCoefficients"]
        wavelength_idxs = range(len(downwelling_light["Pixels"]))
        wavelengths = np.poly1d(wavelength_coeffs[::-1])(wavelength_idxs)
        #TODO: How to get ref data for pico?
        columns = ("wavelength","tgt_count","ref_count","tgt_count_dark",
                "ref_count_dark")
        data = pd.DataFrame(
                columns = columns,
                data = np.array((wavelengths,
                          upwelling_light["Pixels"],
                          downwelling_light["Pixels"],
                          upwelling_dark["Pixels"],
                          downwelling_dark["Pixels"],
                )).T
        )

    if read_metadata:
        metadata = OrderedDict()
        metadata['file'] = f.name
        metadata['instrument_type'] = spectrometer
        metadata['integration_time'] = downwelling_light["Metadata"]["IntegrationTime"]
        for gps_key in PICO_GPS_KEYS:
            if gps_key in downwelling_light:
                metadata['gps_time_ref'] = downwelling_light.get("gps",{}).get("time",None)
                metadata['gps_time_tgt'] = metadata['gps_time_tgt']
        metadata['wavelength_range'] = None
        if read_data:
            metadata['wavelength_range'] = (data.index.min(), data.index.max())
    return data, metadata
