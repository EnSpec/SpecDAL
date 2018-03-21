import pandas as pd
import numpy as np

def proximal_join(base_df, rover_df, on='gps_time_tgt', direction='nearest'):
    '''
    Perform proximal join and return a new dataframe.
    
    Params
    ------
    base_df: pandas.DataFrame
        DataFrame of reference measurements
    
    rover_df: pandas.DataFrame
        DataFrame of target measurements 
    
    Returns
    -------
    proximal: pandas.DataFrame object
        proximally processed dataset ( rover_df / base_df )

    Notes
    -----
    
    As a side-effect, the rover dataframe is sorted by the key
    Both base_df and rover_df must have the column specified by on. 
    This column must be the same type in base and rover.
    '''
    rover_wvl_cols, rover_meta_cols = get_column_types(rover_df)
    base_wvl_cols, base_meta_cols = get_column_types(base_df)
    # join the (sorted) keys
    joined = pd.merge_asof(rover_df[on].sort_values().reset_index(),
                           base_df[on].sort_values().reset_index(),
                           on=on,
                           direction=direction,
                           suffixes=('_rover', '_base'))
    rover_df = rover_df.loc[joined['index_rover']]
    base_df = base_df.loc[joined['index_base']]
    base_df.index = rover_df.index
    metadata = pd.merge(rover_df[rover_meta_cols], base_df[base_meta_cols],
                        left_index=True, right_index=True,
                        suffixes=('_rover', '_base'))
    proximal = rover_df[rover_wvl_cols]/base_df[base_wvl_cols]
    proximal = pd.merge(metadata, proximal, left_index=True,
                        right_index=True) # retrieve metadata
    return proximal


