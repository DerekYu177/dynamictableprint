"""
Tests utils
"""

import unittest
import pandas as pd
from dynamictableprint.utils import max_width_for

class TestPublicFunctions(unittest.TestCase):
    """
    Tests the public module functions
    """

    def setUp(self):
        length = 30

        self.raw_data = {
            'column_name_longest': ["A"*2 for i in range(length)],
            'data_name_longer': ["B"*20 for i in range(length)],
        }

        self.dataframe = pd.DataFrame(self.raw_data)

    def test_max_width_for_when_title_longest(self):
        """
        Tests whether #max_width_for returns when the column name
        is wider than the column itself
        """
        max_length = max_width_for(self.dataframe, 'column_name_longest')
        self.assertEqual(max_length, len('column_name_longest'))

    def test_max_width_for_when_data_name_longest(self):
        """
        Tests whether #max_width_for returns correctly the width
        of the column
        """
        max_length = max_width_for(self.dataframe, 'data_name_longer')
        self.assertEqual(max_length, 20)

if __name__ == '__main__':
    unittest.main()
