"""
Tests the table print extra module
"""

import unittest
from unittest import mock
import pandas as pd

from dynamictableprint.dynamicprinter import DynamicTablePrint

def mock_terminal_size(_):
    """
    Does what it says
    """
    return [102]

class TestDynamicTablePrint(unittest.TestCase):
    """
    Tests the wrapper DynamicTablePrint
    """
    def setUp(self):
        length = 30
        raw_data = {
            'something_good': ["FOOD"*2 for i in range(length)],
            'something_bad': ["WORK"*20 for i in range(length)],
            'squished': ["SQUISHABLE"*4 for i in range(length)],
            'saved': ["CANADA"*3 for i in range(length)],
        }
        dataframe = pd.DataFrame(
            raw_data,
            columns=[*raw_data],
        )
        self.auco = DynamicTablePrint(
            dataframe,
            angel_column='saved',
            squish_column='squished',
        )

    @mock.patch('os.get_terminal_size', side_effect=mock_terminal_size)
    def test_fit_screen(self, _os_function):
        screen_width, widths, _modified_dataframe = self.auco.fit_screen()
        self.assertEqual(screen_width, 100)
        self.assertEqual((10, 52, 26, 12), widths)

if __name__ == '__main__':
    unittest.main()
