# pylint: disable=import-error

import pandas as pd

def safe_int(s):
    return int(s) if s else 0

def dataframe_from_gspread_sheet(sheet, converter=str, **kwargs):
    rows = sheet.get_all_values()
    columns = [c.strip() for c in rows[0]]
    data = [map(converter, row) for row in rows[1:]]
    return pd.DataFrame.from_records(data, columns=columns, **kwargs)
