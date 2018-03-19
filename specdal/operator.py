# Operator.py defines operations on pd.Series that consists of
# wavelength as index and measurement as values
import pandas as pd
import numpy as np
from .utils.misc import get_monotonic_series

################################################################################
# Series operators (single spectrum)
################################################################################

################################################################################
# interpolate: interpolate at given spacing
def interpolate(series, spacing=1, method='slinear'):
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

def _stitch_region(series,wnum,idx,method='max'):
    #the radiances to the left of the negative step
    left_idx = wnum.loc[:idx-1][wnum.loc[:idx-1]>wnum[idx]].index
    #the radiances to the right of the negative step
    right_idx = wnum.loc[idx:][wnum.loc[idx:]<wnum[idx-1]].index
    #sort the wavenumbers on both sides of the jump
    mixed_wnum = sorted(set(series.iloc[left_idx[0]:right_idx[-1]].index))
    #interpolate the radiances on the left side to the full range
    left_rads = series.iloc[left_idx].reindex(mixed_wnum).interpolate(
            limit_direction='both')
    #interpolate the radiances on the right side to the full range
    right_rads = series.iloc[right_idx].reindex(mixed_wnum).interpolate(
            limit_direction='both')
    #apply the stitching method
    if method == 'mean':
        merged = pd.concat([left_rads,right_rads],axis=1).mean(axis=1)
    elif method == 'max':
        merged = pd.concat([left_rads,right_rads],axis=1).max(axis=1)
    elif method == 'min':
        merged =  pd.concat([left_rads,right_rads],axis=1).min(axis=1)
    else:
        raise NotImplementedError

    assert (pd.Series(merged.index).diff()[1:]>0).all()
    return pd.concat([series.iloc[0:left_idx[0]-1],merged,
        series.iloc[right_idx[-1]+1:]])

################################################################################
# stitch: resolve overlaps in wavelengths
def stitch(series, method='max'):
    """
    Stitch the regions with overlapping wavelength
    
    Parameters
    ----------
    series: pandas.Series object
    
    """
    #find indices of overlap
    while (pd.Series(series.index).diff()[1:]<=0).any():
        wnum = pd.Series(series.index)
        wnum_step = wnum.diff()
        neg_idx = wnum.index[wnum_step < 0]
        series = _stitch_region(series,wnum,neg_idx[0],method)
    

    return series
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

