# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=missing-function-docstring missing-module-docstring import-error

import pytest
import pandas as pd

from brioche import PftBiomeMapping, PftTaxaMapping

def test_create_pft_biome_mapping():
    pft_biomes = PftBiomeMapping(pd.DataFrame.from_records(
        columns=('PFT', 'Biome A', 'Biome B'),
        data=[
            (1, 0, 1),
            (2, 1, 1),
            (3, 0, 0),
            ]))

    result = sorted(pft_biomes.mapping.to_dict('records'), key=lambda d: (d['PFT'], d['biome']))

    assert result == [
        dict(PFT=1, biome='Biome A', biome_has_pft=0),
        dict(PFT=1, biome='Biome B', biome_has_pft=1),
        dict(PFT=2, biome='Biome A', biome_has_pft=1),
        dict(PFT=2, biome='Biome B', biome_has_pft=1),
        dict(PFT=3, biome='Biome A', biome_has_pft=0),
        dict(PFT=3, biome='Biome B', biome_has_pft=0),
    ]


def test_create_pft_taxa_mapping():
    pft_taxas = PftTaxaMapping(pd.DataFrame.from_records(
        columns=('PFT', 'Taxa A', 'Taxa B'),
        data=[
            (1, 1, 0),
            (2, 0, 1),
            (3, 1, 1),
            ]))
            
    result = sorted(pft_taxas.mapping.to_dict('records'), key=lambda d: (d['PFT'], d['taxa']))

    assert result == [
        dict(PFT=1, taxa='Taxa A', taxa_in_pft=1),
        dict(PFT=1, taxa='Taxa B', taxa_in_pft=0),
        dict(PFT=2, taxa='Taxa A', taxa_in_pft=0),
        dict(PFT=2, taxa='Taxa B', taxa_in_pft=1),
        dict(PFT=3, taxa='Taxa A', taxa_in_pft=1),
        dict(PFT=3, taxa='Taxa B', taxa_in_pft=1),
    ]


@pytest.mark.parametrize('mapping_class', [PftBiomeMapping, PftTaxaMapping])
def test_matrix_must_contain_pft_column(mapping_class):
    data = pd.DataFrame.from_records(
        columns=('PFFT', 'Column1', 'Column2'),
        data=[(1, 0, 1)])

    with pytest.raises(ValueError):
        mapping_class(data)


@pytest.mark.parametrize('mapping_class', [PftBiomeMapping, PftTaxaMapping])
def test_mapping_must_contain_only_1_and_0(mapping_class):
    data = pd.DataFrame.from_records(
        columns=('PFFT', 'Column1', 'Column2'),
        data=[(1, 2, -1)])

    with pytest.raises(ValueError):
        mapping_class(data)


@pytest.mark.parametrize('mapping_class', [PftBiomeMapping, PftTaxaMapping])
def test_pft_key_name_can_be_changed(mapping_class):
    data = pd.DataFrame.from_records(
        columns=('PFFT', 'Column1', 'Column2'),
        data=[(1, 0, 1)])

    result = mapping_class(data, pft_key='PFFT')
    assert result.pft_key == 'PFFT'
