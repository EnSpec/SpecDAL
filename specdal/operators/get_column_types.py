import pandas as pd
import numpy as np

def get_column_types(df):
    '''
    Returns a tuple (wvl_cols, meta_cols), given a dataframe.
    
    Notes
    -----
    Wavelength column is defined as columns with a numerical name (i.e. decimal).
    Everything else is considered metadata column.
    '''
    isdigit = df.columns.map(str).str.replace('.', '').str.isdigit()
    wvl_cols = df.columns[isdigit].sort_values()
    meta_cols = df.columns.difference(wvl_cols)
    return wvl_cols, meta_cols
