import os
import sys
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import unittest

sys.path.insert(0, os.path.abspath("../../"))
from specdal.spectrum import Spectrum

class spectrumTests(unittest.TestCase):
    def setUp(self):
        pass
    def test_spectrum_read(self):
        s1 = Spectrum(name='s1',
                     filepath='../../../data/aidan_data2/ASD/ACPA_F_A_SU_20160617_00004.asd')
        s2 = Spectrum(name='s2',
                     filepath='../../../data/aidan_data2/PSR/ACPA_F_A_SU_20160617_00002.sed')
        s3 = Spectrum(name='s3',
                     filepath='../../../data/aidan_data2/SVC/ACPA_F_B_SU_20160617_003.sig')
    def test_spectrum_set_measurement(self):
        measurement1 = pd.Series([1, 2, 3, 4], index=pd.Index([1, 2, 3, 4], name='wavelength'),
                                name='pct_reflect')
        measurement2 = pd.Series([3, 0, 1], index=pd.Index([2, 3, 4], name='wavelength'),
                                name='pct_reflect')
        s1 = Spectrum(name='s1', measurement=measurement1)
        s2 = Spectrum(name='s2', measurement=measurement2)
def main():
    unittest.main()


if __name__ == "__main__":
    main()
