"""
The worker module which calculates the columns widths
and modifies the table accordingly
"""

import copy

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
                self._sdf.loc[index, column] = self._squish_to(value, ideal_length)

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
        line = str(line)

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
        return [col for col in [self.squish, *self._non_priority_columns()] if col is not None]

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

    @staticmethod
    def _is_blank(measurement):
        if measurement is None:
            return False

        return True

    def is_blank(self, measurements):
        """
        Returns true if all values in the measurements iterator
        are empty
        """
        filtered = filter(self._is_blank, measurements)
        if not filtered:
            return True

        return False

    def squish_columns(self):
        """
        Squishes the columns to fit within the allocated_width
        """
        if self.is_blank(self.column_measurements):
            return self.column_measurements

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
