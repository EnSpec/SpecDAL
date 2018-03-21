from .split_good_bad import split_good_bad

def filter_threshold(collection,wavelength0,wavelength1,low,high,group='mean'):
    """Filter the spectra from collection that have a value outside of
    (low,high). 
    """
    data = collection.data.loc[wavelength0:wavelength1]
    if group == 'mean':
        mean = data.mean(axis=0)
        good = (mean < high) & (mean > low)
    if group == 'median':
        med = data.median(axis=0)
        good = (med < high) & (med > low)
    if group == 'min':
        _min = data.min(axis=0)
        good = (_min < high) & (_min > low)
    if group == 'max':
        _max = data.max(axis=0)
        good = (_max < high) & (_max > low)
    return split_good_bad(collection,good)
