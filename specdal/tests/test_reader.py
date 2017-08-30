import os
import sys
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import unittest

sys.path.insert(0, os.path.abspath("../../"))
from specdal.reader import read_asd, read_sig, read_sed

class readerTests(unittest.TestCase):
    def setUp(self):
        pass
    def test_asd_reader(self):
        data, meta = read_asd('/data/specdal/data/aidan_data2/ASD/ACPA_F_A_SU_20160617_00001.asd')
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)
    def test_sig_reader(self):
        data, meta = read_sig('/data/specdal/data/aidan_data2/SVC/ACPA_F_A_SU_20160617_002.sig')
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)
    def test_sed_reader(self):
        data, meta = read_sed('/data/specdal/data/aidan_data2/PSR/ACPA_F_A_SU_20160617_00005.sed')
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)
    def test_asd_reader_data(self):
        data, meta = read_asd('/data/specdal/data/aidan_data2/ASD/ACPA_F_A_SU_20160617_00001.asd',
                              read_data=True, read_metadata=False, verbose=False)
        self.assertTrue(data is not None)
        self.assertTrue(meta is None)
    def test_sig_reader_data(self):
        data, meta = read_sig('/data/specdal/data/aidan_data2/SVC/ACPA_F_A_SU_20160617_002.sig',
                              read_data=True, read_metadata=False, verbose=False)
        self.assertTrue(data is not None)
        self.assertTrue(meta is None)
    def test_sed_reader_data(self):
        data, meta = read_sed('/data/specdal/data/aidan_data2/PSR/ACPA_F_A_SU_20160617_00005.sed',
                              read_data=True, read_metadata=False, verbose=False)
        self.assertTrue(data is not None)
        self.assertTrue(meta is None)
    def test_asd_reader_metadata(self):
        data, meta = read_asd('/data/specdal/data/aidan_data2/ASD/ACPA_F_A_SU_20160617_00001.asd',
                              read_data=False, read_metadata=True, verbose=False)
        self.assertTrue(data is None)
        self.assertTrue(meta is not None)
    def test_sig_reader_metadata(self):
        data, meta = read_sig('/data/specdal/data/aidan_data2/SVC/ACPA_F_A_SU_20160617_002.sig',
                              read_data=False, read_metadata=True, verbose=False)
        self.assertTrue(data is None)
        self.assertTrue(meta is not None)
    def test_sed_reader_metadata(self):
        data, meta = read_sed('/data/specdal/data/aidan_data2/PSR/ACPA_F_A_SU_20160617_00005.sed',
                              read_data=False, read_metadata=True, verbose=False)
        self.assertTrue(data is None)
        self.assertTrue(meta is not None)
    def test_read_asd(self):
        data, meta = read_asd('/data/specdal/data/aidan_data2/ASD/ACPA_F_A_SU_20160617_00001.asd')
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)
    def test_read_sig(self):
        data, meta = read_sig('/data/specdal/data/aidan_data2/SVC/ACPA_F_A_SU_20160617_002.sig')
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)
    def test_read_sed(self):
        data, meta = read_sed('/data/specdal/data/aidan_data2/PSR/ACPA_F_A_SU_20160617_00005.sed')
        self.assertTrue(data is not None)
        self.assertTrue(meta is not None)

def main():
    unittest.main()


if __name__ == "__main__":
    main()
