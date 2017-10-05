# Operator.py defines operations on pd.Series that consists of
# wavelength as index and measurement as values
import pandas as pd
import numpy as np
from .utils.misc import get_monotonic_series

################################################################################
# Series operators (single spectrum)
################################################################################

################################################################################
# resample: interpolate at given spacing
def resample(series, spacing=1, method='slinear'):
    """
    Interpolate the array into given spacing
    
    Parameters
    ----------
    series: pandas.Series object
    
    """
    seqs = []
    for seq in get_monotonic_series(series):
        int_index = np.round(seq.index)
        # fill in gaps at 1 nm wavelength
        int_index = int_index.reindex(np.arange(int_index.min(),
                                                int_index.max() + 1,
                                                spacing))[0]
        tmp_index = seq.index.union(int_index)
        seq = seq.reindex(tmp_index)
        # interpolate
        seq = seq.interpolate(method=method)
        # select the integer indices
        seqs.append(seq.loc[int_index])
    return pd.concat(seqs).dropna()

################################################################################
# stitch: resolve overlaps in wavelengths
def stitch(series, method='mean'):
    """
    Stitch the regions with overlapping wavelength
    
    Parameters
    ----------
    series: pandas.Series object
    
    """
    
    if method == 'mean':
        return series.groupby(level=0, axis=0).mean()

################################################################################
# jump_correct: resolve jumps in non-overlapping wavelengths
def jump_correct(series, splices, reference, method="additive"):
    """
    Correct for jumps in non-overlapping wavelengths
    
    Parameters
    ----------
    splices: list
        list of wavelength values where jumps occur
    
    reference: int
        position of the reference band (0-based)
    
    """
    if method == "additive":
        return jump_correct_additive(series, splices, reference)

def jump_correct_additive(series, splices, reference):
    """ Perform additive jump correction (ASD) """
    # if asd, get the locations from the metadata
    # stop if overlap exists
    def get_sequence_num(wavelength):
        """ return the sequence id after cutting at splices """
        for i, splice in enumerate(splices):
            if wavelength <= splice:
                return i
        return i+1
    def translate_y(ref, mov, right=True):
        # translates the mov sequence to stitch with ref sequence
        if right:
            diff = ref.iloc[-1] - mov.iloc[0]
        else:
            diff = ref.iloc[0] - mov.iloc[-1]
        mov = mov + diff
        series.update(mov)
    groups = series.groupby(get_sequence_num)
    for i in range(reference, groups.ngroups-1, 1):
        # move sequences on the right of reference
        translate_y(groups.get_group(i),
                    groups.get_group(i+1),
                    right=True)
    for i in range(reference, 0, -1):
        # move sequences on the left of reference
        translate_y(groups.get_group(i),
                    groups.get_group(i-1),
                    right=False)
    return series

################################################################################
# derivative: calculate derivative of a spectrum
def derivative(series):
    '''
    Calculate the spectral derivative. Not Implemented Yet.
    '''
    pass


################################################################################
# DataFrame operations (collection of spectra)
################################################################################
def get_column_types(df):
    '''
    Returns a tuple (wvl_cols, meta_cols), given a dataframe.
    
    Notes
    -----
    Wavelength column is defined as columns with a numerical name (i.e. decimal).
    Everything else is considered metadata column.
    '''
    isdigit = df.columns.map(str).str.replace('.', '').str.isdigit()
    wvl_cols = df.columns[isdigit].sort_values()
    meta_cols = df.columns.difference(wvl_cols)
    return wvl_cols, meta_cols

def proximal_join(base_df, rover_df, on='gps_time_tgt', direction='nearest'):
    '''
    Perform proximal join and return a new dataframe.
    
    Params
    ------
    base_df: pandas.DataFrame
        DataFrame of reference measurements
    
    rover_df: pandas.DataFrame
        DataFrame of target measurements 
    
    Returns
    -------
    proximal: pandas.DataFrame object
        proximally processed dataset ( rover_df / base_df )

    Notes
    -----
    
    As a side-effect, the rover dataframe is sorted by the key
    Both base_df and rover_df must have the column specified by on. 
    This column must be the same type in base and rover.
    '''
    rover_wvl_cols, rover_meta_cols = get_column_types(rover_df)
    base_wvl_cols, base_meta_cols = get_column_types(base_df)
    # join the (sorted) keys
    joined = pd.merge_asof(rover_df[on].sort_values().reset_index(),
                           base_df[on].sort_values().reset_index(),
                           on=on,
                           direction=direction,
                           suffixes=('_rover', '_base'))
    rover_df = rover_df.loc[joined['index_rover']]
    base_df = base_df.loc[joined['index_base']]
    base_df.index = rover_df.index
    metadata = pd.merge(rover_df[rover_meta_cols], base_df[base_meta_cols],
                        left_index=True, right_index=True,
                        suffixes=('_rover', '_base'))
    proximal = rover_df[rover_wvl_cols]/base_df[base_wvl_cols]
    proximal = pd.merge(metadata, proximal, left_index=True,
                        right_index=True) # retrieve metadata
    return proximal

