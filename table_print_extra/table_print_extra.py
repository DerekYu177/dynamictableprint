import os
import copy
import tableprint as tp

class TablePrintAutoColumnFormatter:

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

    def banner(self):
        """
        :Overridable:

        This is the banner printed at the top of the table
        """
        return 'No Banner Set'

    def empty_banner(self):
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
        screen_width, widths = self._fit_screen()

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

    def item_padding(self):
        """
        :Overridable:
        Padding is the difference between the total item width and the screen width
        """
        return 8

    def _fit_screen(self):
        """
        We take the full length of the available screen
        and force the widths to be less than or equal to this

        If the columns naturally fit within the screen width, the we do nothing.
        We will shrink the next largest column until it will fit the correct size
        """
        screen_width = os.get_terminal_size(0)[0]-2

        columns = self.data_frame.columns.values.tolist()

        fixed_columns = copy.copy(columns)

        if self.squish_column is not None:
            column_widths = self._squish_columns_with_squish_column(fixed_columns)
        else:
            column_widths = self._find_column_widths(fixed_columns)

        #TODO;
        """
        Implement protection for angel name
        Maybe we should have an angel name and a squish name...
        """

        widths = tuple([column_widths[column] for column in columns])
        return screen_width, widths

    def _find_column_widths(self, fixed_columns):
        return { column:self._max_width_for(column) for column in
                fixed_columns }

    def _squish_columns_with_squish_column(self, fixed_columns):
        fixed_columns.remove(self.squish_column)
        column_widths = self._find_column_widths(fixed_columns)

        item_width = screen_width - sum(column_widths.values()) - self.item_padding()
        column_widths.update({ self.squish_column:item_width })

        self.data_frame[self.squish_column] = self.data_frame[self.squish_column] \
                .apply(lambda x: self._item_trucation(item_width, x))

        return column_widths

    def _item_trucation(self, width, line):
        return line if len(line) < width else line[:width-3] + '...'

    def _max_width_for(self, item):
        """
        The maximum width of a column is either the maximum size of the strings
        within that column, OR it is the name of the column itself.
        """
        product_width = self.data_frame[item] \
                .apply(lambda x: len(str(x))) \
                .max()

        name_width = len(str(item))
        return max(product_width, name_width)
