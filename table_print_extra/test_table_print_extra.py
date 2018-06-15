import unittest
import pandas as pd
import table_print_extra as tpe
import os
class TestPublicMethods(unittest.TestCase):

    def setUp(self):
        length = 30

        self.raw_data = {
            'column_name_longest': ["A"*2 for i in range(length)],
            'data_name_longer': ["B"*20 for i in range(length)],
        }

        self.dataframe = pd.DataFrame(self.raw_data)

    def test_max_width_for_when_title_longest(self):
        max_length = tpe.max_width_for(self.dataframe, 'column_name_longest')
        self.assertEqual(max_length, len('column_name_longest'))

    def test_max_width_for_when_data_name_longest(self):
        max_length = tpe.max_width_for(self.dataframe, 'data_name_longer')
        self.assertEqual(max_length, 20)

# class TestTablePrintAutoColumnFormatter(unittest.TestCase):
#     def setUp(self):
#         length = 30
#         raw_data = {
#             'column_name_longest': ["A"*2 for i in range(length)],
#             'data_name_longer': ["B"*20 for i in range(length)],
#             'squished': ["GARBAGE"*4 for i in range(length)],
#             'saved': ["IMPORTANTS"*3 for i in range(length)],
#         }
#         dataframe = pd.DataFrame(raw_data)
#         self.auco = tpe.TablePrintAutoColumnFormatter(
#             dataframe,
#             'saved',
#             squish_column='squished',
#         )
#
#     def test_fit_screen(self):
#         screen_width, widths = self.auco.fit_screen()
#         self.assertEqual(screen_width, os.get_terminal_size(0)[0]-2)

class TestSquisher(unittest.TestCase):
    pass

class TestSquishCalculator(unittest.TestCase):
    def test_single_column_unchanged(self):
        original_columns = {'a': 100}
        s = tpe.SquishCalculator(100, original_columns)
        squished_columns = s.squish_columns()
        self.assertEqual(squished_columns, original_columns)

    def test_squish_column_squishes(self):
        o_columns = {'normal': 20, 'squishable': 16}
        s = tpe.SquishCalculator(34, o_columns, squish='squishable')
        s_columns = s.squish_columns()
        o_columns.update({'squishable': 14})
        self.assertEqual(s_columns, o_columns)

    def test_squish_columns_squishes_more_than_first(self):
        o_columns = {'a':100, 'b':100, 'angel':200}
        s = tpe.SquishCalculator(360, o_columns, angel='angel')
        s_columns = s.squish_columns()
        o_columns.update({'a':80, 'b':80, 'angel':200})
        self.assertEqual(s_columns, o_columns)

    def test_squish_columns_starts_with_squish(self):
        o_columns = {'a':10, 'b':10, 'c':10, 'squish':20, 'angel':100}
        s = tpe.SquishCalculator(148, o_columns, angel='angel', squish='squish')
        s_columns = s.squish_columns()
        o_columns.update({'squish':18})
        self.assertEqual(s_columns, o_columns)

    def test_squish_columns_does_regular_after_squish(self):
        o_columns = {'a':10, 'b':10, 'c':10, 'squish':20, 'angel':100}
        s = tpe.SquishCalculator(142, o_columns, angel='angel', squish='squish')
        s_columns = s.squish_columns()
        o_columns.update({'squish':16, 'a':8, 'b':8})
        self.assertEqual(s_columns, o_columns)

    def test_squish_columns_ends_with_angel(self):
        o_columns = {'a':10, 'b':10, 'c':10, 'squish':20, 'angel':100}
        s = tpe.SquishCalculator(121, o_columns, angel='angel', squish='squish')
        s_columns = s.squish_columns()
        o_columns.update({'squish':16, 'a':8, 'b':8, 'c':8, 'angel':81})
        self.assertEqual(s_columns, o_columns)

if __name__ == '__main__':
    unittest.main()
