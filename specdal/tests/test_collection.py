import os
import sys
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import unittest
from collections import OrderedDict
sys.path.insert(0, os.path.abspath("../../"))
from specdal.spectrum import Spectrum
from specdal.collection import Collection, proximal_join, df_to_collection

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
    def test_collection_data_with_meta(self):
        m1 = OrderedDict()
        m2 = OrderedDict()
        m3 = OrderedDict()
        for i, meta in enumerate([m1, m2, m3]):
            meta['file'] = 'f{}'.format(i)
            meta['instrument_type'] = 'asd'
            meta['integration_time'] = '15'
            meta['measurement_type'] = 'pct_reflect'
            meta['gps_time'] = (100 + i, 200 + i)
            meta['wavelength_range'] = (1, 4)
        s1 = Spectrum(name='s1',
                      measurement= pd.Series([1, 2, 3, 4],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'),
                      metadata=m1)
        s2 = Spectrum(name='s2',
                      measurement= pd.Series([10, 11, 12, 13],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'),
                      metadata=m2)
        s3 = Spectrum(name='s3',
                      measurement= pd.Series([100, 200, 300, 400],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'),
                      metadata=m3)
        c1 = Collection(name='c1', spectra=[s1, s2, s3])
        c1.data_with_meta()
        # TODO: test correctness
    def test_df_to_collection(self):
        df = pd.DataFrame({'file':['f1', 'f2', 'f3'],
                           'gps_time':[1, 2, 3],
                           '500':[.1, .2, .3],
                           '501':[11, 22, 33]},
                          index=['s1', 's2', 's3'])
        c = df_to_collection(df, name='c1')
        for s in c.spectra:
            self.assertEqual(df.loc[s.name]['file'], s.metadata['file'])
            self.assertEqual(df.loc[s.name]['gps_time'], s.metadata['gps_time'])
            self.assertEqual(df.loc[s.name]['500'], s.measurement.loc['500'])
            self.assertEqual(df.loc[s.name]['501'], s.measurement.loc['501'])
    def test_df_to_collection_without_metadata(self):
        df = pd.DataFrame({'500':[.1, .2, .3],
                           '501':[11, 22, 33]},
                          index=['s1', 's2', 's3'])
        c = df_to_collection(df, name='c1')
        for s in c.spectra:
            self.assertEqual(df.loc[s.name]['500'], s.measurement.loc['500'])
            self.assertEqual(df.loc[s.name]['501'], s.measurement.loc['501'])
    def test_df_to_collection_without_measurements(self):
        df = pd.DataFrame({'file':['f1', 'f2', 'f3'],
                           'gps_time':[1, 2, 3]},
                          index=['s1', 's2', 's3'])
        c = df_to_collection(df, name='c1')
        for s in c.spectra:
            self.assertEqual(df.loc[s.name]['file'], s.metadata['file'])
            self.assertEqual(df.loc[s.name]['gps_time'], s.metadata['gps_time'])
    def test_proximal_join(self):
        s1 = Spectrum(name='s1',
                      measurement= pd.Series([1, 2, 3, 4],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'),
                      metadata={'gps_time_tgt':1})
        s2 = Spectrum(name='s2',
                      measurement= pd.Series([10, 11, 12, 13],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'),
                      metadata={'gps_time_tgt':5})
        s3 = Spectrum(name='s3',
                      measurement= pd.Series([100, 200, 300, 400],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'),
                      metadata={'gps_time_tgt':10})
        base = Collection(name='base', spectra=[s1, s2, s3])
        s4 = Spectrum(name='s4',
                      measurement= pd.Series([1, 2, 3, 4],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'),
                      metadata={'gps_time_tgt':2})
        s5 = Spectrum(name='s5',
                      measurement= pd.Series([10, 11, 12, 13],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'),
                      metadata={'gps_time_tgt':5})
        s6 = Spectrum(name='s6',
                      measurement= pd.Series([100, 200, 300, 400],
                                             index=pd.Index([1, 2, 3, 4],
                                                            name='wavelength'),
                                             name='pct_reflect'),
                      metadata={'gps_time_tgt':9})
        rover = Collection(name='rover', spectra=[s4, s5, s6])
        proximal = proximal_join(base, rover)
        proximal_df_correct = pd.DataFrame({'s4':[1.0, 1.0, 1.0, 1.0],
                                            's5':[1.0, 1.0, 1.0, 1.0],
                                            's6':[1.0, 1.0, 1.0, 1.0]},
                                           index=pd.Index([1, 2, 3, 4],
                                                          name='wavelength'))
        pdt.assert_frame_equal(proximal.data, proximal_df_correct)
        


def main():
    unittest.main()
            
if __name__ == "__main__":
    main()
