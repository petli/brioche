# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=import-error

from __future__ import annotations

import pandas as pd
import gspread
import openpyxl

class MappingBase:
    key_name: str = None
    
    def __init__(self, mapping: pd.DataFrame):
        if self.key_name not in mapping.columns:
            raise ValueError('Mapping must have column {}'.format(self.key_name))

        if 'pft' not in mapping.columns:
            raise ValueError('Mapping must have column pft')
        
        self._mapping = mapping

    @property
    def mapping(self) -> pd.DataFrame: 
        """
        Returns the mapping as a DataFrame containing one row for each pair of mapped taxa/biome and PFT. 
        """
        return self._mapping
    

class BiomePftMapping(MappingBase):
    key_name = 'biome'


class TaxaPftMapping(MappingBase):
    key_name = 'taxa'


class BiomePftMatrix(BiomePftMapping):
    def __init__(self, matrix: pd.DataFrame):
        """
        Initialize a biome x pft mapping from a DataFrame containing a mapping matrix.
        It must contain a column called biome that identifies the biomes, and one column
        for each PFT. The cells should contain 1 if the PFT maps to the biome, 0 otherwise.

        Args:
            matrix (pd.DataFrame): The matrix to be converted to a mapping.
        """
        super().__init__(convert_matrix_to_mapping(matrix, self.key_name))


class TaxaPftMatrix(TaxaPftMapping):
    def __init__(self, matrix: pd.DataFrame):
        """
        Initialize a taxa x pft mapping from a DataFrame containing a mapping matrix.
        It must contain a column called taxa that identifies the taxa, and one column
        for each PFT. The cells should contain 1 if the taxa maps to the PFT, 0 otherwise.

        Args:
            matrix (pd.DataFrame): The matrix to be converted to a mapping.
        """
        super().__init__(convert_matrix_to_mapping(matrix, self.key_name))


class PftListBase:
    @staticmethod
    def _convert_list_to_mapping(df: pd.DataFrame, key_name:str) -> pd.DataFrame:
        df = clean_column_name(df, 0, key_name)
        df = clean_column_name(df, 1, 'pft')
        return df.explode('pft')

    @classmethod
    def read_csv(cls, filepath_or_buffer, **kwargs) -> PftListBase:
        """
        Reads a CSV file into a mapping. 
        
        The file should not have any header row. The first column of each row contains
        the taxa or biome, the following columns contain one mapped PFT each.

        Args:
            filepath_or_buffer (str or file-like object): The file path or buffer to read the CSV data from.
            **kwargs: Additional keyword arguments to pass to pandas.read_csv.

        Returns:
            PftListBase: An instance of PftListBase containing the processed CSV data.
        """
        key_name = cls.key_name # pylint: disable=no-member
        raw = pd.read_csv(filepath_or_buffer, dtype=str, header=None, **kwargs)
        df_list = raw.apply(lambda row: pd.Series([row.iloc[0], row.iloc[1:].dropna().to_list()], index=[key_name, 'pft']), axis='columns')
        return cls(df_list)

    @classmethod
    def read_google_sheet(cls, worksheet: gspread.worksheet.Worksheet) -> PftListBase:
        """
        Reads data from a Google Sheets worksheet and returns it as a PftListBase object.

        The worksheet should not have any header row. The first column of each row contains
        the taxa or biome, the following columns contain one mapped PFT each.
        
        Args:
            worksheet (gspread.worksheet.Worksheet): The Google Sheets worksheet to read from.

        Returns:
            PftListBase: An object containing the data from the worksheet.
        """
        key_name = cls.key_name # pylint: disable=no-member
        rows = [(row[0], list(filter(None, row[1:]))) for row in worksheet.get_all_values(value_render_option='UNFORMATTED_VALUE')]
        return cls(pd.DataFrame.from_records(rows, columns=(key_name, 'pft')))

    @classmethod
    def read_excel_sheet(cls, worksheet: openpyxl.worksheet.worksheet.Worksheet) -> PftListBase:
        """
        Reads data from an Excel worksheet and returns it as a PftListBase object.

        The worksheet should not have any header row. The first column of each row contains
        the taxa or biome, the following columns contain one mapped PFT each.
        
        Args:
            worksheet (openpyxl.worksheet.worksheet.Worksheet): The Excel worksheet to read from.

        Returns:
            PftListBase: An object containing the data from the worksheet.
        """
        key_name = cls.key_name # pylint: disable=no-member
        rows = [(row[0], [int(pft) for pft in list(filter(None, row[1:]))]) for row in worksheet.values]
        return cls(pd.DataFrame.from_records(rows, columns=(key_name, 'pft')))


class BiomePftList(BiomePftMapping, PftListBase):
    def __init__(self, df: pd.DataFrame):
        """
        Initialize a biome x pft mapping from a DataFrame containing two columns:
         - biome: biome names
         - pft: lists of pfts that map to the biomes

        Args:
            df (pd.DataFrame): The DataFrame to be converted to a mapping.
        """
        super().__init__(self._convert_list_to_mapping(df, self.key_name))


class TaxaPftList(TaxaPftMapping, PftListBase):
    def __init__(self, df: pd.DataFrame):
        """
        Initialize a taxa x pft mapping from a DataFrame containing two columns:
         - taxa: taxa names
         - pft: lists of pfts that map to the taxa

        Args:
            df (pd.DataFrame): The DataFrame to be converted to a mapping.
        """
        super().__init__(self._convert_list_to_mapping(df, self.key_name))


def clean_column_name(df: pd.DataFrame, index: str, name: str):
    """Check that the column has the expected name (case insensitive)
    as a sanity check that the user provided the right data, 
    and return a new dataframe with the column renamed to the preferred casing.
    """
    df_name = str(df.columns[index])

    if df_name.lower() != name:
        raise ValueError('Column {} in the dataframe must be called "{}"'.format(index + 1, name))

    return df.rename(columns={ df_name: name })


def convert_matrix_to_mapping(matrix: pd.DataFrame, key_name: str):
    matrix = clean_column_name(matrix, 0, key_name)

    # Convert the matrix into a list of relations between biomes/taxas and PFTs
    mapping = matrix.melt(id_vars=[key_name], var_name='pft', value_name='has_pft')
    return mapping[mapping.has_pft == 1].filter(items=[key_name, 'pft'])


