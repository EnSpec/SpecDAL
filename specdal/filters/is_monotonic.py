import pandas as pd
def is_monotonic(collection):
    try:
        return (pd.Series(collection.data.index).diff()[1:]>0).all()
    except:
        return False
