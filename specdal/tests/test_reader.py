import os
import sys
import glob
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import unittest

sys.path.insert(0, os.path.abspath("../../"))
from specdal.reader import read_asd, read_sig, read_sed, read_pico

ASD_FNAME = "/media/mwestphall/2TB/Big_Bio/Big_Bio_2015/LeafLevel/07202015/ASD/_164_4_LESCA_1_T_1_00001.asd"
SIG_FNAME = "/media/mwestphall/2TB/Big_Bio/Big_Bio_2015/LeafLevel/07192015/SVC/136_1_ANDGE_1_B_1_000.sig"
SED_PSRPLS_FNAME = "/media/mwestphall/2TB/Big_Bio/Big_Bio_2015/LeafLevel/07102015/PSR+/149_1_ANDGE_1_M_1__00013.sed"
SED_PSM_FNAME = "/media/mwestphall/2TB/Big_Bio/Big_Bio_2015/LeafLevel/06302015/PSM/157_1_AGRSM_1_M_1__00205.sed"
PICO_FNAME = "/media/mwestphall/2TB/pdata/spectra/20170831-121053_untitled_bat0000__0000.pico.light"

class readerTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_asd_reader(self):
        data, meta = read_asd(ASD_FNAME)
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)
    def test_sig_reader(self):
        data, meta = read_sig(SIG_FNAME)
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)
    def test_sed_reader(self):
        data, meta = read_sed(SED_PSM_FNAME)
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)

    def test_pico_reader(self):
        data, meta = read_pico(PICO_FNAME)
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)

    def test_asd_reader_data(self):
        data, meta = read_asd(ASD_FNAME,
                              read_data=True, read_metadata=False, verbose=False)
        self.assertTrue(data is not None)
        self.assertTrue(meta is None)

    def test_sig_reader_data(self):
        data, meta = read_sig(SIG_FNAME,
                              read_data=True, read_metadata=False, verbose=False)
        self.assertTrue(data is not None)
        self.assertTrue(meta is None)
    def test_sed_reader_data(self):
        data, meta = read_sed(SED_PSM_FNAME,
                              read_data=True, read_metadata=False, verbose=False)
        self.assertTrue(data is not None)
        self.assertTrue(meta is None)

    def test_pico_reader_data(self):
        data, meta = read_pico(PICO_FNAME,
                              read_data=True, read_metadata=False, verbose=False)
        self.assertTrue(data is not None)
        self.assertTrue(meta is None)
    
    def test_asd_reader_metadata(self):
        data, meta = read_asd(ASD_FNAME,
                              read_data=False, read_metadata=True, verbose=False)
        self.assertTrue(data is None)
        self.assertTrue(meta is not None)
    def test_sig_reader_metadata(self):
        data, meta = read_sig(SIG_FNAME,
                              read_data=False, read_metadata=True, verbose=False)
        self.assertTrue(data is None)
        self.assertTrue(meta is not None)
    def test_sed_reader_metadata(self):
        data, meta = read_sed(SED_PSM_FNAME,
                              read_data=False, read_metadata=True, verbose=False)
        self.assertTrue(data is None)
        self.assertTrue(meta is not None)

    def test_pico_reader_metadata(self):
        data, meta = read_pico(PICO_FNAME,
                              read_data=False, read_metadata=True, verbose=False)
        self.assertTrue(data is None)
        self.assertTrue(meta is not None)
    '''
    def test_read_asd(self):
        data, meta = read_asd(ASD_FNAME, meta = read_sig(SIG_FNAME'/data/specdal/data/aidan_data2/SVC/ACPA_F_A_SU_20160617_002.sig')
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)
    def test_read_sed(self):
        data, meta = read_sed(SED_PSRPLS_FNAME,'/data/specdal/data/aidan_data2/PSR/ACPA_F_A_SU_20160617_00005.sed')
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)
    '''
def main():
    unittest.main()


if __name__ == "__main__":
    main()
