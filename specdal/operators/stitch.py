# Operator.py defines operations on pd.Series that consists of
# wavelength as index and measurement as values
import pandas as pd
import numpy as np

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

