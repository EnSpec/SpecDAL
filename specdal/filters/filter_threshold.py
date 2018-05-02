from .split_good_bad import split_good_bad

def filter_threshold(collection,wavelength0,wavelength1,low,high,group='mean'):
    """Filter the spectra from collection that have a value outside of
    (low,high). 
    Parameters
    ----------
    collection: specdal.containers.collection.Collection
        the collection to filter
   
    wavelength0: float
        the starting wavelength to filter

    wavelength1: float
        the ending wavelength to filter 

    low: float
        minimum allowed value between wavelength0 and wavelength1

    high: float
        maximum allowed value between wavelength0 and wavelength1

    group: string
        if there are multiple data points between wavelength0 and wavelength1, 
        average them this way. Options: "mean", "median", "min", "max"

    Returns
    -------
    good: specdal.containers.Collection
        A new collection made of the spectra that passed the filter

    bad: specdal.containers.Collection
        A new collection made of the spectra that failed the filter
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
