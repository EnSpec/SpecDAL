import os
import sys
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import unittest

sys.path.insert(0, os.path.abspath("../../"))
from specdal.operator import resample

class resamplerTests(unittest.TestCase):
    def setUp(self):
        pass
    def test_index_without_gap(self):
        s1 = pd.DataFrame({'measurement':[1, 2, 3, 4],
                           'wavelength':[0.8, 2.1, 2.9, 4]}).set_index(
                                        'wavelength')['measurement']
        s1_pre = resample(s1)
        pdt.assert_index_equal(s1_pre.index,
                               pd.Index([1, 2, 3, 4],
                                        name='wavelength', dtype=float))
    def test_index_with_gap(self):
        s1 = pd.DataFrame({'measurement':[1, 2, 3, 4],
                           'wavelength':[0.8, 3.1, 6, 8]}).set_index(
                                        'wavelength')['measurement']
        s1_pre = resample(s1)
        pdt.assert_index_equal(s1_pre.index,
                               pd.Index([1, 2, 3, 4, 5, 6, 7, 8],
                                        name='wavelength', dtype=float))
    def test_index_with_gap_spacing(self):
        s1 = pd.DataFrame({'measurement':[1, 2, 3, 4],
                           'wavelength':[0.8, 3.1, 6, 8]}).set_index(
                                        'wavelength')['measurement']
        s1_pre = resample(s1, spacing=2)
        pdt.assert_index_equal(s1_pre.index,
                               pd.Index([1, 3, 5, 7],
                                        name='wavelength', dtype=float))

def main():
    unittest.main()


if __name__ == "__main__":
    main()


