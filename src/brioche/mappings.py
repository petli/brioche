# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

class MappingBase:
    def __init__(self, mapping):
        if self.key_name not in mapping.columns:
            raise ValueError('Mapping must have column {}'.format(self.key_name))

        if 'pft' not in mapping.columns:
            raise ValueError('Mapping must have column pft')
        
        if self.value_name not in mapping.columns:
            raise ValueError('Mapping must have column {}'.format(self.value_name))

        if not mapping[self.value_name].isin([0, 1]).all():
            raise ValueError('Mapping values must only contain values 0 or 1')

        self._mapping = mapping

    @property
    def mapping(self): return self._mapping

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


class BiomePftMatrix(BiomePftMapping):
    def __init__(self, matrix):
        super().__init__(convert_matrix_to_mapping(matrix, self.key_name, self.value_name))


class TaxaPftMatrix(TaxaPftMapping):
    def __init__(self, matrix):
        super().__init__(convert_matrix_to_mapping(matrix, self.key_name, self.value_name))

def convert_matrix_to_mapping(matrix, key_name, value_name):
    input_key = str(matrix.columns[0])

    # We could be flexible here, but this provides a sanity check that we got the right matrix
    if input_key.lower() != key_name:
        raise ValueError('The first column in the matrix must be called "{}"'.format(key_name))

    # Convert the matrix into a list of relations between biomes/taxas and PFTs
    mapping = matrix.melt(id_vars=[input_key], var_name='pft', value_name=value_name)

    # Rename the first column to the exact name, to get rid of any capitalization
    mapping.rename(columns={ input_key: key_name }, inplace=True)

    return mapping

