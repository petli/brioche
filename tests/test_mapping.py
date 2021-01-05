# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=missing-function-docstring missing-module-docstring import-error

import pytest
import pandas as pd

from brioche import BiomePftMatrix, TaxaPftMatrix, BiomePftList, TaxaPftList

def test_create_pft_biome_matrix():
    pft_biomes = BiomePftMatrix(pd.DataFrame.from_records(
        columns=('Biome', 1, 2, 3),
        data=[
            ('Biome A', 0, 1, 0),
            ('Biome B', 1, 1, 0)
            ]))

    result = sorted(pft_biomes.mapping.to_dict('records'), key=lambda d: (d['pft'], d['biome']))

    assert result == [
        dict(pft=1, biome='Biome B'),
        dict(pft=2, biome='Biome A'),
        dict(pft=2, biome='Biome B'),
    ]


def test_create_pft_taxa_matrix():
    pft_taxas = TaxaPftMatrix(pd.DataFrame.from_records(
        columns=('Taxa', 1, 2, 3),
        data=[
            ('Taxa A', 1, 0, 1),
            ('Taxa B', 0, 1, 1)
            ]))
            
    result = sorted(pft_taxas.mapping.to_dict('records'), key=lambda d: (d['pft'], d['taxa']))

    assert result == [
        dict(pft=1, taxa='Taxa A'),
        dict(pft=2, taxa='Taxa B'),
        dict(pft=3, taxa='Taxa A'),
        dict(pft=3, taxa='Taxa B'),
    ]


@pytest.mark.parametrize('mapping_class', [BiomePftMatrix, TaxaPftMatrix])
def test_matrix_must_contain_key_column(mapping_class):
    data = pd.DataFrame.from_records(
        columns=('foo', 1, 2),
        data=[('bar', 0, 1)])

    with pytest.raises(ValueError):
        mapping_class(data)


def test_create_biome_pft_list():
    biome_pfts = BiomePftList(pd.DataFrame.from_records(
        columns=('Biome', 'PFT'),
        data=[
            ('Biome A', [2, 3]),
            ('Biome B', [1, 2])
            ]))

    result = sorted(biome_pfts.mapping.to_dict('records'), key=lambda d: (d['pft'], d['biome']))

    assert result == [
        dict(pft=1, biome='Biome B'),
        dict(pft=2, biome='Biome A'),
        dict(pft=2, biome='Biome B'),
        dict(pft=3, biome='Biome A')
    ]


def test_create_taxa_pft_list():
    taxa_pfts = TaxaPftList(pd.DataFrame.from_records(
        columns=('Taxa', 'PFT'),
        data=[
            ('Taxa A', [3, 1]),
            ('Taxa B', [4, 1])
            ]))

    result = sorted(taxa_pfts.mapping.to_dict('records'), key=lambda d: (d['pft'], d['taxa']))

    assert result == [
        dict(pft=1, taxa='Taxa A'),
        dict(pft=1, taxa='Taxa B'),
        dict(pft=3, taxa='Taxa A'),
        dict(pft=4, taxa='Taxa B'),
    ]
