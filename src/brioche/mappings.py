# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=import-error

import pandas as pd

class MappingBase:
    key_name = None
    
    def __init__(self, mapping):
        if self.key_name not in mapping.columns:
            raise ValueError('Mapping must have column {}'.format(self.key_name))

        if 'pft' not in mapping.columns:
            raise ValueError('Mapping must have column pft')
        
        self._mapping = mapping

    @property
    def mapping(self): return self._mapping

class BiomePftMapping(MappingBase):
    key_name = 'biome'


class TaxaPftMapping(MappingBase):
    key_name = 'taxa'


class BiomePftMatrix(BiomePftMapping):
    def __init__(self, matrix):
        super().__init__(convert_matrix_to_mapping(matrix, self.key_name))


class TaxaPftMatrix(TaxaPftMapping):
    def __init__(self, matrix):
        super().__init__(convert_matrix_to_mapping(matrix, self.key_name))


class PftListBase:
    @staticmethod
    def _convert_list_to_mapping(df, key_name):
        df = clean_column_name(df, 0, key_name)
        df = clean_column_name(df, 1, 'pft')
        return df.explode('pft')

    @classmethod
    def read_csv(cls, filepath_or_buffer, **kwargs):
        key_name = cls.key_name # pylint: disable=no-member
        raw = pd.read_csv(filepath_or_buffer, dtype=str, header=None, **kwargs)
        df_list = raw.apply(lambda row: pd.Series([row.iloc[0], row.iloc[1:].dropna().to_list()], index=[key_name, 'pft']), axis='columns')
        return cls(df_list)

    @classmethod
    def read_google_sheet(cls, worksheet):
        key_name = cls.key_name # pylint: disable=no-member
        rows = [(row[0], list(filter(None, row[1:]))) for row in worksheet.get_all_values(value_render_option='UNFORMATTED_VALUE')]
        return cls(pd.DataFrame.from_records(rows, columns=(key_name, 'pft')))


class BiomePftList(BiomePftMapping, PftListBase):
    def __init__(self, df):
        super().__init__(self._convert_list_to_mapping(df, self.key_name))


class TaxaPftList(TaxaPftMapping, PftListBase):
    def __init__(self, df):
        super().__init__(self._convert_list_to_mapping(df, self.key_name))


def clean_column_name(df, index, name):
    """Check that the column has the expected name (case insensitive)
    as a sanity check that the user provided the right data, 
    and return a new dataframe with the column renamed to the preferred casing.
    """
    df_name = str(df.columns[index])

    if df_name.lower() != name:
        raise ValueError('Column {} in the dataframe must be called "{}"'.format(index + 1, name))

    return df.rename(columns={ df_name: name })


def convert_matrix_to_mapping(matrix, key_name):
    matrix = clean_column_name(matrix, 0, key_name)

    # Convert the matrix into a list of relations between biomes/taxas and PFTs
    mapping = matrix.melt(id_vars=[key_name], var_name='pft', value_name='has_pft')
    return mapping[mapping.has_pft == 1].filter(items=[key_name, 'pft'])


