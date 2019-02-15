import unittest, sys, io, pandas as pd, sqlite3
from contextlib import redirect_stdout
from unittest.mock import patch
from hw4 import *
import hw4
from compare_pandas import *

''' 
Auxiliary files needed:
    classes_redacted.db
    compare_pandas.py
    all_countries0.pkl, all_countries1.pkl, all_countries2.pkl, all_countries3.pkl, dying.pkl
This one is needed by hw4.py and is therefore required:
    countries_of_the_world.csv
'''

class TestFns(unittest.TestCase):
    def setUp(self):
        self.regs = ['western europe', 'eastern europe', 'northern america', 'sub-saharan africa']
        self.reg_dict = {r:[] for r in self.regs}
        self.world0 = pd.read_pickle('all_countries0.pkl') # after csv_to_dataframe
        self.world1 = pd.read_pickle('all_countries1.pkl') # after format_df
        self.world2 = pd.read_pickle('all_countries2.pkl') # after life_change
        self.world3 = pd.read_pickle('all_countries3.pkl') # after years_to_extinction
        for w in [self.world0, self.world1, self.world2, self.world3]:
            for i in range(len(self.regs)):
                self.reg_dict[self.regs[i]].append(w[w['Region'].str.strip().str.lower() == self.regs[i]])
   
    def test_csv_to_dataframe(self):
        correct = pd.read_pickle('all_countries0.pkl')
        tester = csv_to_dataframe('countries_of_the_world.csv')
        self.assertTrue(compare_frames_str(correct, tester))
        
    def test_format_df(self):
        correct = pd.read_pickle('all_countries1.pkl')
        df = pd.read_pickle('all_countries0.pkl')
        self.assertIsNone(format_df(df))
        self.assertTrue(compare_frames_str(correct, df))
    
    def test_growth_rate(self):
        correct = pd.read_pickle('all_countries2.pkl')
        df = pd.read_pickle('all_countries1.pkl')
        self.assertIsNone(growth_rate(df))
        self.assertTrue(compare_frames_str(correct, df))
    
    def test_years_to_extinction(self):
        correct = pd.read_pickle('all_countries3.pkl')
        df = pd.read_pickle('all_countries2.pkl')
        self.assertIsNone(years_to_extinction(df))
        self.assertTrue(compare_frames_str(correct, df))
    
    def test_dying_countries(self):
        correct = pd.read_pickle('dying.pkl')
        df = pd.read_pickle('all_countries3.pkl')
        self.assertTrue(compare_series(correct, dying_countries(df)))
    
    def test_class_performance(self):
        conn = sqlite3.connect('classes_redacted.db')
        entries = [{'A': 29.3, 'B': 8.6, 'F': 17.2, 'R': 20.7, 'U': 24.1},  #conn
                   {'A': 22.9, 'B': 16.7, 'F': 22.9, 'R': 22.9, 'U': 14.6}, #350_s15
                   {'A': 17.0, 'B': 25.2, 'F': 16.3, 'R': 19.3, 'U': 22.2}, #130_s15
                   {'A': 27.7, 'B': 17.0, 'F': 21.3, 'R': 23.4, 'U': 10.6}, #120_f16
                   {'A': 26.1, 'B': 13.0, 'F': 23.9, 'R': 19.6, 'U': 17.4}] #350_s18
    
        self.assertEqual(entries[0], class_performance(conn))
        self.assertEqual(entries[1], class_performance(conn, 'ista_350_s15'))
        self.assertEqual(entries[2], class_performance(conn, 'ista_130_s15'))
        self.assertEqual(entries[3], class_performance(conn, 'ista_120_f16'))
        self.assertEqual(entries[4], class_performance(conn, 'ista_350_s18'))
    
    def test_improved(self):
        conn = sqlite3.connect('classes_redacted.db')
        entries = {('ista_131_f17', 'ista_130_s17'): ['Foxobuc', 'Liyafeg', 
                    'Mijasaz', 'Nojomes', 'Popocoj', 'Poxozih', 'Saxigot', 
                    'Strocitit', 'Thalewuw', 'Thocerog', 'Thocoyof', 'Xiqiyas',
                    'Yirawox', 'Zoweqoh', 'Zugetoj'],
                   ('ista_130_f17', 'ista_130_s18'): ['Suwarij', 'Yimayuw'],
                   ('ista_130_f17', 'ista_350_s18'): ['Fipugax', 'Roruvor', 
                    'Wabiwow', 'Xaruliy', 'Yugator'],
                   ('ista_130_f17', 'ista_130_s17'): []}
        for key in entries:
            self.assertEqual(entries[key], improved(conn, key[0], key[1]))
    
    def test_main(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            res = 'Botswana: 2115.0 Years to Extinction\n' +\
            'Monaco: 2602.0 Years to Extinction\n' +\
            'Ukraine: 3038.0 Years to Extinction\n' +\
            'Latvia: 3148.0 Years to Extinction\n' +\
            'Bulgaria: 3266.0 Years to Extinction\n'
            hw4.main()
            self.assertEqual(res, buf.getvalue())
    
def main():
    test = unittest.defaultTestLoader.loadTestsFromTestCase(TestFns)
    results = unittest.TextTestRunner().run(test)
    print('Correctness score = ', str((results.testsRun - len(results.errors) - len(results.failures)) / results.testsRun * 100) + ' / 100')
    
if __name__ == "__main__":
    main()