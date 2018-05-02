# Operator.py defines operations on pd.Series that consists of
# wavelength as index and measurement as values
import pandas as pd
import numpy as np

def get_monotonic_series(series):
    """return a list of series with monotonic index
    
    TODO: test what happens if not strictly monotonic
        i.e. index: 1, 2, 3, 3
    """
    if series.index.is_monotonic:
        return [series]
    else:
        index = pd.Series(series.index)
        head_positions = index[index.diff() < 0].index

        N = head_positions.size
        
        result = [series.iloc[:head_positions[0]]]
        result += [series.iloc[head_positions[i]:head_positions[i+1]] for i in range(0, N-1)]
        result += [series.iloc[head_positions[N-1]:]]
        return result

# interpolate: interpolate at given spacing
def interpolate(series, spacing=1, method='slinear'):
    """
    Interpolate the array into given spacing
    
    Parameters
    ----------
    series: pandas.Series object

    spacing: int
        wavelength spacing to interpolate at (in nm)

    method: string
        "slinear" or "cubic"
    
    """
    seqs = []
    for seq in get_monotonic_series(series):
        int_index = np.round(seq.index)
        # fill in gaps at 1 nm wavelength
        int_index = int_index.reindex(np.arange(int_index.min(),
                                                int_index.max() + 1,
                                                spacing))[0]
        tmp_index = seq.index.union(int_index)
        seq = seq.reindex(tmp_index)
        # interpolate
        seq = seq.interpolate(method=method)
        # select the integer indices
        seqs.append(seq.loc[int_index])
    return pd.concat(seqs).dropna()
