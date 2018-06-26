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

    def determine_screen_width(self, screen_width):
        if screen_width is not None:
            return screen_width
        else:
            try:
                # subtract two so that we get some spacing
                screen_width = os.get_terminal_size(0)[0] - 2
            except OSError:
                screen_width = self.config.default_screen_width

        return screen_width

    def __init__(self, data_frame, angel_column=None, squish_column=None,
            screen_width=None):
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

        self.config = DefaultConfig()

        self.screen_width = self.determine_screen_width(screen_width)

        self.squish_calculator = SquishCalculator
        self.squisher = DataFrameSquisher

    def write_to_screen(self):
        """
        The key method to this class
        prints the data frame in a nice manner which scales to the terminal size
        available to the user.
        """
        screen_width, widths, modified_data_frame = self.fit_screen()

        tp.banner(
            self.config.banner,
            width=screen_width,
        )

        if self.data_frame.empty:
            tp.banner(
                self.config.empty_banner,
                width=screen_width,
            )

        tp.dataframe(modified_data_frame, width=widths)

    @staticmethod
    def printable_screen_width(columns, screen_width):
        """
        Calculates the total amount of printable real estate
        Takes into acccount the columns and gaps between them
        """
        number_columns = len(columns)
        screen_width_exc_side_bars = screen_width - 2 # bar and space
        screen_width_inc_columns = screen_width_exc_side_bars \
            - 3 * (number_columns - 1)
        return screen_width_inc_columns

    def fit_screen(self):
        """
        We take the full length of the available screen
        and force the widths to be less than or equal to this

        If the columns naturally fit within the screen width, the we do nothing.
        We will shrink the next largest column until it will fit the correct size
        """
        columns = self.data_frame.columns.values.tolist()
        column_widths = find_column_widths(self.data_frame, columns)

        printable_screen_width = self.printable_screen_width(
            columns, self.screen_width)

        calculator = self.squish_calculator(
            printable_screen_width,
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
        return self.screen_width, printing_widths, modified_dataframe

class DefaultConfig:
    """
    Holds the data for configuration
    We use __slots__ to prevent ourselves from modifying this
    object outside of the class
    """
    __slots__ = [
        "banner",
        "empty_banner",
        "item_padding",
        "default_screen_width",
    ]

    def __init__(self):
        self.default_screen_width = 80

        """ Banner printed at the top of the table """
        self.banner = 'No Banner Set'

        """ Banner when there is no content """
        self.empty_banner = 'Error: No results'

        """ Difference between the total item width and the screen width """
        self.item_padding = 8
