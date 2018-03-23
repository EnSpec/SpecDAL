from specdal.containers.collection import Collection,df_to_collection

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

