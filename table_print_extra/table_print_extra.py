"""
This module aims to add extra functionality to the already amazing
TablePrint.

Use Case:
We have a pandas table, and the user wants the table to have columns that
fit the size of the string data. If there are many columns, the
TablePrintAutoColumnFormatter will look at the available screen
real estate, and squish columns to fit, while still perserving readability
overall.
"""

import os
import copy
import tableprint as tp

def max_width_for(frame, item):
    """
    The maximum width of a column is either the maximum size of the strings
    within that column, OR it is the name of the column itself.
    """
    product_width = frame[item] \
            .apply(lambda x: len(str(x))) \
            .max()

    name_width = len(str(item))
    return max(product_width, name_width)

def _find_column_widths(data_frame, fixed_columns):
    return {column:max_width_for(data_frame, column) for column in
            fixed_columns}

class TablePrintAutoColumnFormatter:
    """
    This is the wrapper class around TablePrint, which does the formatting
    """

    def __init__(self, data_frame, angel_column, squish_column=None):
        """
        data_frame is a DataFrame

        The angel_column is a string which matches a column.
        This column will be protected from the dynamic shrinking that will occur

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
        screen_width, widths = self.fit_screen()

        tp.banner(
            self.banner(),
            width=screen_width
        )

        if self.data_frame.empty:
            tp.banner(
                'ERROR: No results',
                width=screen_width
            )

        tp.dataframe(self.data_frame, width=widths)

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
    def squisher():
        """
        :Overridable: (also not necessary)
        The squishing object which performs the modifiation to the object
        """
        return Squisher()

    def fit_screen(self):
        """
        We take the full length of the available screen
        and force the widths to be less than or equal to this

        If the columns naturally fit within the screen width, the we do nothing.
        We will shrink the next largest column until it will fit the correct size
        """
        screen_width = os.get_terminal_size(0)[0]-2

        columns = self.data_frame.columns.values.tolist()
        column_widths = _find_column_widths(self.data_frame, columns)

        calculator = self.squish_calculator(
            screen_width,
            column_widths,
            squish=self.squish_column,
            angel=self.angel_column,
        )
        fitted_column_widths = calculator.squish_columns()
        modified_column_widths = self.squisher().squish(fitted_column_widths,
                                                        self.data_frame)

        widths = tuple([modified_column_widths[column] for column in columns])
        return screen_width, widths

class Squisher:

    """
    Takes the column data, and squishes the columns based on that
    """

    __ellipses = '...'

    def squish(self, requested_column_size, dataframe):
        """
        Modifies the column data
        """
        for column, amount in requested_column_size.items():
            self._squish_column_by(dataframe[column], amount)

        return dataframe

    def set_ellipses(self, new_ellipses):
        """
        The only responsible way to set ellipses
        """
        self.__ellipses = new_ellipses

    def _squish_column_by(self, column, squish_amount):
        column = column.apply(lambda x: self._squish_by(x, squish_amount))

    def _squish_by(self, line, amount):
        truncated_line = line[:len(line)-amount]
        return truncated_line[:len(truncated_line)-len(self.__ellipses)] + self.__ellipses

class SquishCalculator:
    """
    Squishes and formats the columns data, but does not touch the
    data frame itself
    """

    def __init__(self, allocated_width, column_measurements,
                 squish=None, angel=None):

        self.__max_squish_ratio = 0.2
        self.allocated_width = allocated_width

        # god damn reference
        self.column_measurements = copy.copy(column_measurements)
        self.squish = squish
        self.angel = angel

    def _within_allocated_width(self):
        return self._calculate_column_width() <= self.allocated_width

    def _calculate_column_width(self):
        return sum(self.column_measurements.values())

    def _non_priority_columns(self):
        return [c_name for c_name in list(self.column_measurements) if c_name
                not in [self.squish, self.angel]]

    def _squish_order(self):
        return [col for col in [self.squish, *self._non_priority_columns(),
                                self.angel] if col is not None]

    def _update_column_measurements(self, target, squish_amount):
        self.column_measurements[target] = self.column_measurements[target] - squish_amount

    def _find_squish_ratio(self, target):
        target_width = self.column_measurements[target]
        squish_amount = self._calculate_column_width() - self.allocated_width
        squish_ratio = squish_amount / float(target_width)
        return squish_ratio, squish_amount

    def _squish_by_ratio(self, target):
        return int(self.column_measurements[target] * self.__max_squish_ratio)

    def set_max_squish_ratio(self, new_ratio):
        """
        Only responsible way to set this value
        """
        self.__max_squish_ratio = new_ratio

    def squish_columns(self):
        """
        Squishes the columns to fit within the allocated_width
        """
        for column in self._squish_order():

            if self._within_allocated_width():
                return self.column_measurements

            s_ratio, s_amount = self._find_squish_ratio(column)

            if s_ratio >= self.__max_squish_ratio:
               s_amount = self._squish_by_ratio(column)

            self._update_column_measurements(
                column,
                s_amount
            )

        return self.column_measurements
