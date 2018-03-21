# Operator.py defines operations on pd.Series that consists of
# wavelength as index and measurement as values
import pandas as pd
import numpy as np

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

