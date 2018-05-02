from .split_good_bad import split_good_bad

def filter_std(collection,wavelength0,wavelength1,std_thresh,group='mean'):
    """Filter the spectra from collection that have a standard deviation
    outside a certain threshold.

    Parameters
    ----------
    collection: specdal.containers.collection.Collection
        the collection to filter
   
    wavelength0: float
        the starting wavelength to filter

    wavelength1: float
        the ending wavelength to filter 

    std_thresh: float
        remove spectra outside of std_thresh standard deviations from the mean

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
    #extract the relevant wavelength range
    data = collection.data.loc[wavelength0:wavelength1]
    mean = data.mean(axis=1)
    std = data.std(axis=1)
    #number of standard deviations from mean at each wavelength
    n_std = data.sub(mean,axis=0).div(std,axis=0).abs()

    if group == 'mean':
        good = n_std.mean() < std_thresh
    if group == 'median':
        good = n_std.median() < std_thresh
    if group == 'min':
        good = n_std.min() < std_thresh
    if group == 'max':
        good = n_std.min() < std_thresh
    #TODO: work around transposing
    return split_good_bad(collection,good)

