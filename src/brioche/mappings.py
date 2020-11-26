# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

from .helpers import dataframe_from_gspread_sheet, safe_int

class MappingBase:
    def __init__(self, matrix):
        input_key = str(matrix.columns[0])

        # We could be flexible here, but this provides a sanity check that we got the right matrix
        if input_key.lower() != self.key_name:
            raise ValueError('The first column in the {} matrix must be called "{}"'.format(self.__class__.__name__, self.key_name))

        # Convert the matrix into a list of relations between biomes/taxas and PFTs
        self.mapping = matrix.melt(id_vars=[input_key], var_name='pft', value_name=self.value_name)

        if not self.mapping[self.value_name].isin([0, 1]).all():
            raise ValueError('Mapping matrix cells must only contain values 0 or 1')

        # Rename the first column to the exact name, to get rid of any capitalization
        self.mapping.rename(columns={ input_key: self.key_name }, inplace=True)

    @classmethod
    def from_gspread_sheet(cls, sheet):
        return cls(dataframe_from_gspread_sheet(sheet, converter=safe_int, first_value_column=1))

    @property
    def key_name(self): raise NotImplementedError()

    @property
    def value_name(self): raise NotImplementedError()


class BiomePftMapping(MappingBase):
    @property
    def key_name(self): return 'biome'

    @property
    def value_name(self): return 'biome_has_pft'


class TaxaPftMapping(MappingBase):
    @property
    def key_name(self): return 'taxa'

    @property
    def value_name(self): return 'taxa_in_pft'

