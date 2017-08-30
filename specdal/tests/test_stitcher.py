import os
import sys
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import unittest

sys.path.insert(0, os.path.abspath("../../"))
from specdal.spectrum import Spectrum
from specdal.operator import stitch

class stitcherTests(unittest.TestCase):
    def setUp(self):
        pass
    def test_operator_stitcher_mean(self):
        measurement= pd.Series([100, 200, 300, 400, 500],
                               index=pd.Index([1, 2, 3, 3, 4],
                                              name='wavelength'),
                               name='pct_reflect')
        measurement_stitched = pd.Series([100, 200, 350, 500],
                                         index=pd.Index([1, 2, 3, 4],
                                                        name='wavelength'),
                                         name='pct_reflect')
        pdt.assert_series_equal(stitch(measurement), measurement_stitched)
        
    def test_spectrum_stitcher_mean(self):
        s1 = Spectrum(name='s1',
                      measurement= pd.Series([100, 200, 300, 400, 500],
                                             index=pd.Index([1, 2, 3, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'))
        measurement_stitched = pd.Series([100, 200, 350, 500],
                                         index=pd.Index([1, 2, 3, 4],
                                                        name='wavelength'),
                                         name='pct_reflect')
        s1.stitch()
        pdt.assert_series_equal(s1.measurement, measurement_stitched)
        
def main():
    unittest.main()
            
if __name__ == "__main__":
    main()
