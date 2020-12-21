# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

class MappingBase:
    def __init__(self, mapping):
        if self.key_name not in mapping.columns:
            raise ValueError('Mapping must have column {}'.format(self.key_name))

        if 'pft' not in mapping.columns:
            raise ValueError('Mapping must have column pft')
        
        self._mapping = mapping

    @property
    def mapping(self): return self._mapping

    @property
    def key_name(self): raise NotImplementedError()


class BiomePftMapping(MappingBase):
    @property
    def key_name(self): return 'biome'


class TaxaPftMapping(MappingBase):
    @property
    def key_name(self): return 'taxa'


class BiomePftMatrix(BiomePftMapping):
    def __init__(self, matrix):
        super().__init__(convert_matrix_to_mapping(matrix, self.key_name))


class TaxaPftMatrix(TaxaPftMapping):
    def __init__(self, matrix):
        super().__init__(convert_matrix_to_mapping(matrix, self.key_name))


class BiomePftList(BiomePftMapping):
    def __init__(self, list):
        super().__init__(convert_list_to_mapping(list, self.key_name))


class TaxaPftList(TaxaPftMapping):
    def __init__(self, list):
        super().__init__(convert_list_to_mapping(list, self.key_name))


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


def convert_list_to_mapping(list, key_name):
    list = clean_column_name(list, 0, key_name)
    list = clean_column_name(list, 1, 'pft')
    return list.explode('pft')
