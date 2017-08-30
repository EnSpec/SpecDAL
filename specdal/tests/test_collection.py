import os
import sys
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import unittest

sys.path.insert(0, os.path.abspath("../../"))
from specdal.spectrum import Spectrum
from specdal.collection import Collection

class collectionTests(unittest.TestCase):
    def setUp(self):
        pass
    def test_collection_assert_unique_name1(self):
        s1 = Spectrum(name='s1',
                      measurement= pd.Series([1, 2, 3, 4],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'))
        s2 = Spectrum(name='s1',
                      measurement= pd.Series([1, 2, 3, 4],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'))
        self.assertRaises(AssertionError, Collection, name='c1', spectra=[s1, s2])
    def test_collection_assert_unique_name1(self):
        s1 = Spectrum(name='s1',
                      measurement= pd.Series([1, 2, 3, 4],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'))
        s2 = Spectrum(name='s1',
                      measurement= pd.Series([1, 2, 3, 4],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'))
        c1 = Collection(name='c1')
        c1.append(s1)
        self.assertRaises(AssertionError, c1.append, s2)
    def test_collection_data_unstitched(self):
        s1 = Spectrum(name='s1',
                      measurement= pd.Series([1, 2, 3, 4],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'))
        s2 = Spectrum(name='s2',
                      measurement= pd.Series([10, 11, 12, 13],
                                             index=pd.Index([0.8, 2.2, 3.7, 5],
                                                            name='wavelength'),
                                             name='pct_reflect'))
        s3 = Spectrum(name='s3',
                      measurement= pd.Series([100, 200, 300, 400, 500],
                                             index=pd.Index([1, 2, 3, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'))
        c1 = Collection(name='c1', spectra=[s1, s2, s3])
        self.assertRaises(ValueError, lambda: c1.data)
        c1.stitch()
        print(c1.data)
        
def main():
    unittest.main()
            
if __name__ == "__main__":
    main()
