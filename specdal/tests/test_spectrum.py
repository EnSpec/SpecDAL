import os
import sys
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import unittest

sys.path.insert(0, os.path.abspath("../../"))
from specdal.spectrum import Spectrum

ASD_FNAME = "/media/mwestphall/2TB/Big_Bio/Big_Bio_2015/LeafLevel/07202015/ASD/_164_4_LESCA_1_T_1_00001.asd"
SIG_FNAME = "/media/mwestphall/2TB/Big_Bio/Big_Bio_2015/LeafLevel/07192015/SVC/136_1_ANDGE_1_B_1_000.sig"
SED_PSRPLS_FNAME = "/media/mwestphall/2TB/Big_Bio/Big_Bio_2015/LeafLevel/07102015/PSR+/149_1_ANDGE_1_M_1__00013.sed"
SED_PSM_FNAME = "/media/mwestphall/2TB/Big_Bio/Big_Bio_2015/LeafLevel/06302015/PSM/157_1_AGRSM_1_M_1__00205.sed"
PICO_FNAME = "/media/mwestphall/2TB/pdata/spectra/20170831-121053_untitled_bat0000__0000.pico.light"

class spectrumTests(unittest.TestCase):
    def setUp(self):
        pass
    def test_spectrum_read(self):
        s1 = Spectrum(name='s1',
                     filepath=ASD_FNAME)
        s2 = Spectrum(name='s2',
                     filepath=SED_PSM_FNAME)
        s3 = Spectrum(name='s3',
                     filepath=SIG_FNAME)
        s4 = Spectrum(name='s4',
                     filepath=PICO_FNAME)

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
