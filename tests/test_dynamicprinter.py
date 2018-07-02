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
    return [80]

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
        self.dataframe = pd.DataFrame.from_dict(
            raw_data,
        )

        self.blank_dataframe = pd.DataFrame.from_dict(
            {
                'stupid': [],
                'idiot': [],
                'how could I forget': [],
                'that blank': [],
                'was a think': [],
            }
        )

        self.auco = DynamicTablePrint(
            self.dataframe,
            angel_column='saved',
            squish_column='squished',
        )

    @mock.patch('os.get_terminal_size', side_effect=mock_terminal_size)
    def test_system_screen_width(self, _os_function):
        """
        Tests that we make the correct call to os.get_terminal_size
        """
        screen_width, _widths, _modified_dataframe = self.auco.fit_screen()
        self.assertEqual(screen_width, 80)

    def test_system_fallback_width(self):
        """
        In the case where we cannot get at the system settings, we set a default
        """
        self.assertEqual(self.auco.screen_width, self.auco.config.default_screen_width)

    def test_settable_screen_width(self):
        """
        User is allowed to set the screen width
        """
        dtp = DynamicTablePrint(self.dataframe, screen_width=100)
        self.assertEqual(dtp.screen_width, 100)

    def test_printable_screen_width(self):
        """
        Ensuring that we have the appropriate amount of space for columns
        """
        default_screen_width = 80
        printable_width = default_screen_width - 2 - 3*3

        assert DynamicTablePrint.printable_screen_width(
            ['something_good', 'something_bad', 'squished', 'saved'],
            default_screen_width) == printable_width

    def test_empty_dataframe(self):
        """
        if printing an empty dataframe, nothing should happen
        """
        dtp = DynamicTablePrint(self.blank_dataframe)
        dtp.config.empty_banner = 'Test in Progress'
        dtp.squish_calculator = mock.MagicMock()
        dtp.write_to_screen()
        dtp.squish_calculator.assert_not_called()

if __name__ == '__main__':
    unittest.main()
