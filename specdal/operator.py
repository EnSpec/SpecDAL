# Operator.py defines operations on pd.Series that consists of
# wavelength as index and measurement as values
import pandas as pd
import numpy as np
from .utils.misc import get_monotonic_series

################################################################################
# resample: interpolate at given spacing
def resample(series, spacing=1, method='slinear'):
    """Interpolate the array into given spacing"""
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
    if method == 'mean':
        return series.groupby(level=0, axis=0).mean()

################################################################################
# jump_correct: resolve jumps in non-overlapping wavelengths
def jump_correct(series, splices, reference, method="additive"):
    """Stitch jumps for non-overlapping wavelengths"""
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
    pass
