#set of functions to automatically identify bad spectra in a collection
#and separate them from the rest

from .collection import Collection,df_to_collection

def split_good_bad(collection,is_good):
    """
    Given: A collection and some error metric
    Return: 2 collections, one of the flagged-good data, one of the flagged-bad
    data
    """
    #TODO: work around transposing
    good_spectra = collection.data.T[is_good]
    bad_spectra = collection.data.T[~is_good]

    good_col = df_to_collection(good_spectra,name=collection.name)
    bad_col = df_to_collection(bad_spectra,name=collection.name+'_filtered')

    return good_col,bad_col

def filter_std(collection,wavelength0,wavelength1,std_thresh,group='mean'):
    """Filter the spectra from collection who have a mean std that is greater
    than std_thresh times the mean std between wavelength0 and wavelength1
    group can be mean, median, max, min. min <-> all, max <-> any
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

def filter_white(collection,wavelength0=0,wavelength1=10000,group='mean'):
    """Filter out white reference spectra from collection"""
    data = collection.data.loc[wavelength0:wavelength1]
    mean = data.mean(axis=0)
    std = data.std(axis=0)
    #a flat-ish spectrum at nearly 1 is probably white
    white = (mean > 0.9) & (mean < 1.1) & (std < .03)
    good = ~white
    if not good.all():
        return split_good_bad(collection,good)
    return collection,Collection(collection.name+'_filtered')

   
