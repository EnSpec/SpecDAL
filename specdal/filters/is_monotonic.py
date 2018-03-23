import pandas as pd
def is_monotonic(collection):
    return (pd.Series(collection.data.index).diff()[1:]>0).all()
