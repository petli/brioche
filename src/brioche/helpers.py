# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=import-error

import pandas as pd
import itertools

def safe_int(s):
    return int(s) if s else 0

def dataframe_from_gspread_sheet(sheet, converter=str, first_value_column=0, **kwargs):
    def convert_column(column, value):
        if column < first_value_column:
            return value
        else:
            return converter(value)

    rows = sheet.get_all_values()
    columns = [c.strip() for c in rows[0]]
    data = [map(convert_column, row) for row in rows[1:]]
    return pd.DataFrame.from_records(data, columns=columns, **kwargs)
