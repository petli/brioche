# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=missing-function-docstring missing-module-docstring import-error

import pytest
import pandas as pd

from brioche import BiomePftMapping, TaxaPftMapping

def test_create_pft_biome_mapping():
    pft_biomes = BiomePftMapping(pd.DataFrame.from_records(
        columns=('Biome', 1, 2, 3),
        data=[
            ('Biome A', 0, 1, 0),
            ('Biome B', 1, 1, 0)
            ]))

    result = sorted(pft_biomes.mapping.to_dict('records'), key=lambda d: (d['pft'], d['biome']))

    assert result == [
        dict(pft=1, biome='Biome A', biome_has_pft=0),
        dict(pft=1, biome='Biome B', biome_has_pft=1),
        dict(pft=2, biome='Biome A', biome_has_pft=1),
        dict(pft=2, biome='Biome B', biome_has_pft=1),
        dict(pft=3, biome='Biome A', biome_has_pft=0),
        dict(pft=3, biome='Biome B', biome_has_pft=0),
    ]


def test_create_pft_taxa_mapping():
    pft_taxas = TaxaPftMapping(pd.DataFrame.from_records(
        columns=('Taxa', 1, 2, 3),
        data=[
            ('Taxa A', 1, 0, 1),
            ('Taxa B', 0, 1, 1)
            ]))
            
    result = sorted(pft_taxas.mapping.to_dict('records'), key=lambda d: (d['pft'], d['taxa']))

    assert result == [
        dict(pft=1, taxa='Taxa A', taxa_in_pft=1),
        dict(pft=1, taxa='Taxa B', taxa_in_pft=0),
        dict(pft=2, taxa='Taxa A', taxa_in_pft=0),
        dict(pft=2, taxa='Taxa B', taxa_in_pft=1),
        dict(pft=3, taxa='Taxa A', taxa_in_pft=1),
        dict(pft=3, taxa='Taxa B', taxa_in_pft=1),
    ]


@pytest.mark.parametrize('mapping_class', [BiomePftMapping, TaxaPftMapping])
def test_matrix_must_contain_key_column(mapping_class):
    data = pd.DataFrame.from_records(
        columns=('foo', 1, 2),
        data=[('bar', 0, 1)])

    with pytest.raises(ValueError):
        mapping_class(data)


@pytest.mark.parametrize('mapping_class', [BiomePftMapping, TaxaPftMapping])
@pytest.mark.parametrize('value', [-1, 2, 0.5])
def test_mapping_must_contain_only_1_and_0(mapping_class, value):
    data = pd.DataFrame.from_records(
        columns=(mapping_class.key_name, 1),
        data=[('foo', value)])

    with pytest.raises(ValueError):
        mapping_class(data)

