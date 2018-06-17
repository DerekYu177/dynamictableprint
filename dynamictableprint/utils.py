"""
Utilities
"""

def max_column_width(column):
    """
    Max width of a column, looping over all column elements
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

def find_column_widths(data_frame, fixed_columns=None):
    """
    Convenience method to loop over all columns
    """
    if fixed_columns is None:
        fixed_columns = data_frame.columns.tolist()

    return {column:max_width_for(data_frame, column) for column in
            fixed_columns}
