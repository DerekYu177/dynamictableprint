"""
The wrapper module around tableprint
"""

import os
import tableprint as tp

from .utils import find_column_widths
from .squisher import DataFrameSquisher, SquishCalculator

class DynamicTablePrint:
    """
    This is the wrapper class around TablePrint, which does the formatting
    for tables of a specific format:

    | title |
    |c|c|c|c|

    This class forces the columns to fit within the constraints of the
    available window
    """

    def __init__(self, data_frame, angel_column=None, squish_column=None):
        """
        data_frame is the Pandas DataFrame object, or an object which will
        respond in the same manner

        The angel_column is a string which matches a column name.
        This column will be the last column to be squished in a single
        iteration

        This is in contrast to the squish column, which is the first
        on any chopping block
        """
        self.data_frame = data_frame
        self.squish_column = squish_column
        self.angel_column = angel_column

    @staticmethod
    def banner():
        """
        :Overridable:

        This is the banner printed at the top of the table
        """
        return 'No Banner Set'

    @staticmethod
    def empty_banner():
        """
        :Overridable:

        What happens when there is no content to display
        """
        return 'ERROR: No results'

    def write_to_screen(self):
        """
        The key method to this class
        prints the data frame in a nice manner which scales to the terminal size
        available to the user.
        """
        screen_width, widths, modified_data_frame = self.fit_screen()

        tp.banner(
            self.banner(),
            width=screen_width
        )

        if self.data_frame.empty:
            tp.banner(
                self.empty_banner(),
                width=screen_width
            )

        tp.dataframe(modified_data_frame, width=widths)

    @staticmethod
    def item_padding():
        """
        :Overridable:
        Padding is the difference between the total item width and the screen width
        """
        return 8

    @staticmethod
    def squish_calculator(allocated_width, column_measurements, squish=None,
                          angel=None):
        """
        :Overridable: (but not necessary)
        The calculator object which computes the necessary column sizes
        """
        return SquishCalculator(
            allocated_width,
            column_measurements,
            squish=squish,
            angel=angel,
        )

    @staticmethod
    def squisher(fitted_column_widths, data_frame):
        """
        :Overridable: (also not necessary)
        The squishing object which performs the modifiation to the object
        """
        return DataFrameSquisher(fitted_column_widths, data_frame)

    def fit_screen(self):
        """
        We take the full length of the available screen
        and force the widths to be less than or equal to this

        If the columns naturally fit within the screen width, the we do nothing.
        We will shrink the next largest column until it will fit the correct size
        """
        screen_width = os.get_terminal_size(0)[0]-2

        columns = self.data_frame.columns.values.tolist()
        column_widths = find_column_widths(self.data_frame, columns)

        calculator = self.squish_calculator(
            screen_width,
            column_widths,
            squish=self.squish_column,
            angel=self.angel_column,
        )
        desired_column_widths = calculator.squish_columns()

        squisher = self.squisher(
            desired_column_widths,
            self.data_frame)

        squisher.squish()
        modified_dataframe = squisher.squished_dataframe

        printing_widths = tuple(desired_column_widths.values())
        return screen_width, printing_widths, modified_dataframe

