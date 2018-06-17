"""
This module aims to add extra functionality to the already amazing
TablePrint.

"""

import os
import copy
import tableprint as tp

def max_column_width(column):
    """
    Max width of a column
    """

    return column \
            .apply(lambda x: len(str(x))) \
            .max()

def max_width_for(frame, item):
    """
    The maximum width of a column is either the maximum size of the strings
    within that column, OR it is the name of the column itself.
    """

    name_width = len(str(item))
    return max(max_column_width(frame[item]), name_width)

def _find_column_widths(data_frame, fixed_columns):
    return {column:max_width_for(data_frame, column) for column in
            fixed_columns}

class DynamicTablePrint:
    """
    This is the wrapper class around TablePrint, which does the formatting
    """

    def __init__(self, data_frame, angel_column=None, squish_column=None):
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
        column_widths = _find_column_widths(self.data_frame, columns)

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

class DataFrameSquisher:
    """
    Takes the column data, and squishes the columns based on that
    """

    __ellipses = '...'

    def __init__(self, requested_column_size, dataframe):
        self.requested_column_size = requested_column_size
        self.dataframe = dataframe
        self.squished_dataframe = copy.deepcopy(dataframe)

        # alias for internal use only
        self._sdf = self.squished_dataframe

    def squish(self):
        """
        Modifies the column data and name of
        squished dataframe only

        Merely a coordinator of the other public methods
        for convienence.
        """
        self.modify_column_data()
        self.modify_column_names()

    def modify_column_data(self):
        """
        Changes the column values based
        on the requested_column_size
        """
        for column in self._sdf.columns:
            ideal_length = self.requested_column_size[column]

            # unable to use apply with lambda since
            # the context changes and self is uncallable
            for index, value in enumerate(self._sdf[column].values):
                self._sdf[column][index] = self._squish_to(value, ideal_length)

    def modify_column_names(self):
        """
        Changes the column names based
        on the requested_column_size
        """
        columns = {}
        for column in self._sdf.columns:
            old_name = column
            new_length = self.requested_column_size[column]
            new_name = self._squish_to(old_name, new_length)
            columns.update({old_name: new_name})

        self._sdf.rename(columns=columns, inplace=True)

    def set_ellipses(self, new_ellipses):
        """
        The only responsible way to set ellipses
        Convention is to be three characters i.e. '...'
        """
        self.__ellipses = new_ellipses

    def _squish_to(self, line, ideal_length):
        if len(line) <= ideal_length:
            return line

        if self.__ideal(line, ideal_length):
            return self._squish_line(line, ideal_length, self.__ellipses)

        ellipses = "." * (ideal_length - 1)
        return self._squish_line(line, ideal_length, ellipses)

    def __ideal(self, line, ideal_length):
        return(
            (len(line) > ideal_length)
            and (ideal_length > len(self.__ellipses))
        )

    @staticmethod
    def _squish_line(line, ideal_length, ellipses):
        truncated_line = line[:ideal_length]
        return truncated_line[:len(truncated_line)-len(ellipses)] + ellipses

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

        if self._within_allocated_width():
            return self.column_measurements

        return self.squish_columns()
