"""
Tests the table print extra module
"""

import unittest
import copy
import os
from unittest import mock as mock
import pandas as pd

from table_print_extra import(
    max_column_width,
    max_width_for,
    SquishCalculator,
    DataFrameSquisher,
    TablePrintAutoColumnFormatter,
)

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

def mock_terminal_size(_):
    """
    Does what it says
    """
    return [102]

class TestTablePrintAutoColumnFormatter(unittest.TestCase):
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
        self.auco = TablePrintAutoColumnFormatter(
            dataframe,
            angel_column='saved',
            squish_column='squished',
        )

    @mock.patch('os.get_terminal_size', side_effect=mock_terminal_size)
    def test_fit_screen(self, os_function):
        screen_width, widths, _modified_dataframe = self.auco.fit_screen()
        self.assertEqual(screen_width, 100)
        self.assertEqual((10, 52, 26, 12), widths)

class TestDataFrameSquisher(unittest.TestCase):
    """
    Tests the Squisher
    """
    def setUp(self):
        length = 30
        raw_data = {
            'column_name_longest': ["A"*2 for i in range(length)],
            'data_name_longer': ["B"*20 for i in range(length)],
            'squished': ["GARBAGE"*4 for i in range(length)],
            'saved': ["IMPORTANTS"*3 for i in range(length)],
        }

        self.dataframe = pd.DataFrame(
            raw_data,
            columns=[*raw_data],
        )
        self.original_dataframe = copy.deepcopy(self.dataframe)
        self.requested_column_size = {
            'column_name_longest': 2,
            'data_name_longer': 13,
            'squished': 20,
            'saved': 27,
        }
        self.df_squisher = DataFrameSquisher(
            self.requested_column_size,
            self.dataframe,
        )

    def test_input_dataframe_unchanged(self):
        """
        This shows that you can pass one dataframe in
        and still maintain a copy of the original dataframe
        """
        self.df_squisher.squish()

        self.assertEqual(
            self.original_dataframe.columns.tolist(),
            self.dataframe.columns.tolist()
        )
        for column in self.original_dataframe.columns:
            self.assertEqual(
                self.original_dataframe[column].tolist(),
                self.dataframe[column].tolist()
            )

    def test_modify_column_names(self):
        """
        Not only to we modify the column names,
        but we maintain the original ordering
        """
        self.df_squisher.modify_column_names()
        columns = self.df_squisher.squished_dataframe.columns.tolist()
        correct_columns = ['c.', 'data_name_...', 'squished', 'saved']
        self.assertEqual(correct_columns, columns)

    def test_modify_column_data(self):
        """
        We modify the column data to the requested size.
        we ascertain that this is correct by
        relying on #max_width_for and by
        relying on column names to be in the correct order
        """
        self.df_squisher.modify_column_data()
        squished_dataframe = self.df_squisher.squished_dataframe
        for index, column in enumerate(squished_dataframe.columns):
            self.assertEqual(
                max_column_width(squished_dataframe[column]),
                [*self.requested_column_size.values()][index]
            )

    def test_squish_squishes(self):
        """
        #squish squishes according to the requested
        column size
        """
        self.df_squisher.squish()
        squished_dataframe = self.df_squisher.squished_dataframe
        for index, column in enumerate(squished_dataframe.columns):
            self.assertEqual(
                max_width_for(squished_dataframe, column),
                [*self.requested_column_size.values()][index]
            )

class TestSquishCalculator(unittest.TestCase):
    """
    Tests the SquishCalculator
    """

    def test_single_column_unchanged(self):
        """
        If nothing is wrong, return the original
        """
        original_columns = {'a': 100}
        calculator = SquishCalculator(100, original_columns)
        squished_columns = calculator.squish_columns()
        self.assertEqual(squished_columns, original_columns)

    def test_squish_column_squishes(self):
        """
        If the solution involves squishing one thing to get the right answer
        Do it
        """
        o_columns = {'normal': 20, 'squishable': 16}
        calculator = SquishCalculator(34, o_columns, squish='squishable')
        s_columns = calculator.squish_columns()
        o_columns.update({'squishable': 14})
        self.assertEqual(s_columns, o_columns)

    def test_squish_columns_squishes_more_than_first(self):
        """
        If the first column doesn't work, continue squishing
        """
        o_columns = {'a':100, 'b':100, 'angel':200}
        calculator = SquishCalculator(360, o_columns, angel='angel')
        s_columns = calculator.squish_columns()
        o_columns.update({'a':80, 'b':80, 'angel':200})
        self.assertEqual(s_columns, o_columns)

    def test_squish_columns_starts_with_squish(self):
        """
        Always start with squishing the squish
        """
        o_columns = {'a':10, 'b':10, 'c':10, 'squish':20, 'angel':100}
        calculator = SquishCalculator(148, o_columns, angel='angel', squish='squish')
        s_columns = calculator.squish_columns()
        o_columns.update({'squish':18})
        self.assertEqual(s_columns, o_columns)

    def test_squish_columns_does_regular_after_squish(self):
        """
        Once you're done squishing the squish, move on to 'non-priority'
        columns
        """
        o_columns = {'a':10, 'b':10, 'c':10, 'squish':20, 'angel':100}
        calculator = SquishCalculator(142, o_columns, angel='angel', squish='squish')
        s_columns = calculator.squish_columns()
        o_columns.update({'squish':16, 'a':8, 'b':8})
        self.assertEqual(s_columns, o_columns)

    def test_squish_columns_ends_with_angel(self):
        """
        Only at the very end, when everything is squished, do you
        go squish the angel
        """
        o_columns = {'a':10, 'b':10, 'c':10, 'squish':20, 'angel':100}
        calculator = SquishCalculator(121, o_columns, angel='angel', squish='squish')
        s_columns = calculator.squish_columns()
        o_columns.update({'squish':16, 'a':8, 'b':8, 'c':8, 'angel':81})
        self.assertEqual(s_columns, o_columns)

    def test_recursive_squishing(self):
        pass

if __name__ == '__main__':
    unittest.main()
