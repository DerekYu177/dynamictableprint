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
        """
        If the user wants to set the screen_width, we abide by that decision
        If not, we use the system configuration
        else, we fallback to the default screen width that is given in the
        DefaultConfig
        """
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
        self.data_frame = data_frame.reset_index(drop=True)
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
            return

        tp.dataframe(modified_data_frame, width=widths)

    @staticmethod
    def printable_screen_width(columns, screen_width):
        """
        Calculates the total amount of printable real estate
        Takes into acccount the columns and gaps between them
        """
        number_columns = len(columns)
        screen_width_exc_side_bars = screen_width - DefaultConfig().edge_width
        screen_width_inc_columns = \
            screen_width_exc_side_bars - 3 * (number_columns - 1)
        return screen_width_inc_columns

    @staticmethod
    def _table_width(column_widths):
        """
        The inverse of printable_screen_width
        Instead of finding the space for text
        We use the text to find the size of the table
        Cast to int since sum(*) yields a numpy.int64
        """
        number_columns = len(column_widths.values())
        table_width = sum(column_widths.values())
        table_width = table_width + DefaultConfig().edge_width
        table_width = table_width + 3 * (number_columns - 1)
        return int(table_width)

    @staticmethod
    def _column_widths(dataframe):
        columns = dataframe.columns.values.tolist()
        column_widths = find_column_widths(dataframe, columns)
        return column_widths, columns

    def fit_screen(self):
        """
        We take the full length of the available screen
        and force the widths to be less than or equal to this
        """
        if self.data_frame.empty:
            return (self.config.default_screen_width,
                    self.config.default_screen_width - self.config.edge_width,
                    self.data_frame)

        column_widths, columns = self._column_widths(self.data_frame)

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
        modified_data_frame = squisher.squished_dataframe

        printing_widths = tuple(desired_column_widths.values())
        table_width = self._table_width(desired_column_widths)

        return table_width, printing_widths, modified_data_frame

class DefaultConfig:
    """
    Holds the data for configuration
    We use __slots__ to prevent ourselves from modifying this
    object outside of the class
    """
    __slots__ = [
        "banner",
        "empty_banner",
        "default_screen_width",
        "edge_width",
    ]

    def __init__(self):
        self.default_screen_width = 80

        """ Banner printed at the top of the table """
        self.banner = 'No Banner Set'

        """ Banner when there is no content """
        self.empty_banner = 'Error: No results'

        """ Width due to spaces on either side of the table"""
        self.edge_width = 2
