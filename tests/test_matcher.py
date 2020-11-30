#!/usr/bin/python
# -*- coding: utf-8 -*-
# to run me, type in terminal: 'python -m unittest tests.test_matcher'
'''Testing for errors in matcher.py'''
import unittest
from purple_haze import matcher
import numpy as np

class MatcherTest(unittest.TestCase):
    '''tests matcher.py for accuracy and errors'''
    # smoke test
    def test_smoke(self):
        '''first, a smoke test to make sure output of matcher.py is not zero'''
		test = 'test'
        assert matcher.count_csv_files(test) is not None

    # one-shot test (add next)

if __name__ == '__main__':
    unittest.main()
