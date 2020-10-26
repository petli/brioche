from .helpers import dataframe_from_gspread_sheet, safe_int

class MappingBase:
    def __init__(self, matrix, pft_key, var_name, value_name):
        if not pft_key in matrix:
            raise ValueError('Matrix does not contain PFT key column "{}"'.format(pft_key))

        self.pft_key = pft_key

        # Convert the matrix into a list of relations between PFTs and biomes/taxas
        self.mapping = matrix.melt(id_vars=[pft_key], var_name=var_name, value_name=value_name)

        if not self.mapping[value_name].isin([0, 1]).all():
            raise ValueError('Mapping matrix cells must only contain values 0 or 1')

    @classmethod
    def from_gspread_sheet(cls, sheet, **kwargs):
        return cls(dataframe_from_gspread_sheet(sheet, converter=safe_int), **kwargs)


class PftBiomeMapping(MappingBase):
    def __init__(self, pft_biome_matrix, pft_key='PFT'):
        super().__init__(pft_biome_matrix, pft_key, 'biome', 'biome_has_pft')


class PftTaxaMapping(MappingBase):
    def __init__(self, pft_taxa_matrix, pft_key='PFT'):
        super().__init__(pft_taxa_matrix, pft_key, 'taxa', 'taxa_in_pft')

