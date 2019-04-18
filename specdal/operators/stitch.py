# Operator.py defines operations on pd.Series that consists of
# wavelength as index and measurement as values
import pandas as pd
import numpy as np
from . import interpolate

def _stitch_zero(series,wnum,idx,method='max'):
    return pd.concat([series.iloc[0:idx],series.iloc[idx+1:]])

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
    elif method == 'first':
        merged = series.iloc[left_idx]
    elif method == 'last':
        merged = serues.iloc[right_idx]
    else:
        raise NotImplementedError

    assert (pd.Series(merged.index).diff()[1:]>0).all()
    return pd.concat([series.iloc[0:left_idx[0]-1],merged,
        series.iloc[right_idx[-1]+1:]])

################################################################################
# stitch: resolve overlaps in wavelengths
def stitch(series, method='max', jump_reference=None):
    """
    Stitch the regions with overlapping wavelength
    
    Parameters
    ----------
    series: pandas.Series object

    method: string
        How to compute final value in case of overlap. "mean","median","min", or "max". 
    
    """
    #find indices of overlap
    
    if method == 'first':
        return stitch_by_intersect(series)
    
    while (pd.Series(series.index).diff()[1:]<=0).any():
        # find non-positive steps in wavenumber index
        wnum = pd.Series(series.index)
        wnum_step = wnum.diff()
        neg_idx = wnum.index[wnum_step <= 0]
        # stitch at the first non-positive index
        if wnum_step[neg_idx[0]] == 0:
            series = _stitch_zero(series,wnum,neg_idx[0],method)
        else:
            series = _stitch_region(series,wnum,neg_idx[0],method)
    
    assert (pd.Series(series.index).diff()[1:] > 0).all(), "Stitched wavenumbers not strictly increasing!"
    return series

def _intersection(p1, p2):
    """Find the intersection of two partially-overlapping series"""
    p1 = interpolate(p1)
    p2 = interpolate(p2)
    diff = p1 - p2
    return (p1 - p2).abs().idxmin() - 1

def _jump_correct(parts,reference_idx):
    """Jump correct a stitch"""
    # jump correct backwards from the reference
    reference = parts[reference_idx]
    for i in range(reference_idx-1,-1,-1):
        jump = parts[i].iloc[-1] - reference.iloc[0]
        parts[i] -= jump
        reference = parts[i]
    # jump correct forwards from the reference
    reference = parts[reference_idx]
    for i in range(reference_idx+1,len(parts)):
        jump = parts[i].iloc[0] - reference.iloc[-1]
        parts[i] -= jump
        reference = parts[i]
    
def stitch_by_intersect(series, jump_reference=1):
    if (pd.Series(series.index).diff()[1:]<=0).any():
        parts = []
        # find non-positive steps in wavenumber index
        wnum = pd.Series(series.index)
        wnum_step = wnum.diff()
        neg_idxs = [0] + list(wnum.index[wnum_step <= 0]) + [None]
        # chop the spectrum up into sections of increasing wavenumber
        for i1, i2 in zip(neg_idxs,neg_idxs[1:]):
            parts.append(series.iloc[i1:i2])
        # find where sections of increasing wavenumber intersect eachother
        bounds = [0] + [_intersection(p1,p2) 
                        for p1, p2 in zip(parts,parts[1:])] + [pd.np.Inf]
        assert len(bounds) == len(parts) + 1
        # truncate sections to the points where they intersect
        truncated_parts = []
        for b0,b1,p in zip(bounds,bounds[1:],parts):
            p = interpolate(p)
            truncated_parts.append(p[(p.index > b0) & (p.index <= b1)])

    if jump_reference is not None:
        _jump_correct(truncated_parts,jump_reference)

    series = pd.concat(truncated_parts)
    assert (pd.Series(series.index).diff()[1:] > 0).all(), "Stitched wavenumbers not strictly increasing!"
    return series
