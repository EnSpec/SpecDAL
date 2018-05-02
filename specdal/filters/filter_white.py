from specdal.containers.collection import Collection,df_to_collection
from .split_good_bad import split_good_bad

def filter_white(collection,wavelength0=0,wavelength1=10000,group='mean'):
    """Filter white reference spectra from collection
    
    Returns
    -------
    good: specdal.containers.Collection
        A new collection made of the spectra that passed the filter

    bad: specdal.containers.Collection
        A new collection made of the spectra that failed the filter
    """
    data = collection.data.loc[wavelength0:wavelength1]
    mean = data.mean(axis=0)
    std = data.std(axis=0)
    #a flat-ish spectrum at nearly 1 is probably white
    white = (mean > 0.9) & (mean < 1.1) & (std < .03)
    good = ~white
    if not good.all():
        return split_good_bad(collection,good)
    return collection,Collection(collection.name+'_filtered')

