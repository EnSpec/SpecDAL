import os
import sys
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
import unittest

sys.path.insert(0, os.path.abspath("../../"))
from specdal.spectrum import Spectrum
from specdal.collection import Collection

class GroupByTests(unittest.TestCase):
    def setUp(self):
        # total 36 spectra
        self.c = Collection(name='For Groups')
        for a in ('A', 'B', 'C'):
            for b in ('a', 'b', 'c'):
                for c in ('0', '1'):
                    for d in ('0001', '0002', '0003', '0004'):
                        self.c.append(Spectrum('_'.join([a, b, c, d])))
        # print([s.name for s in self.c.spectra])

    def test_groups(self):
        groups = self.c.groupby(separator='_', indices=[0, 2])
        for s in groups['A_0'].spectra:
            print(s.name)
    '''
    def test_num_groups(self):
        groups = self.c.groupby(separator='_', indices=[0])
        self.assertEqual(len(groups), 3)
        groups = self.c.groupby(separator='_', indices=[1])
        self.assertEqual(len(groups), 3)
        groups = self.c.groupby(separator='_', indices=[2])
        self.assertEqual(len(groups), 4)
        groups = self.c.groupby(separator='_', indices=[0, 1])
        self.assertEqual(len(groups), 9)
        groups = self.c.groupby(separator='_', indices=[0, 2])
        self.assertEqual(len(groups), 12)
        groups = self.c.groupby(separator='_', indices=[1, 2])
        self.assertEqual(len(groups), 12)
        groups = self.c.groupby(separator='_', indices=[0, 1, 2])
        self.assertEqual(len(groups), 36)
    '''
def main():
    unittest.main()


if __name__ == '__main__':
    main()
