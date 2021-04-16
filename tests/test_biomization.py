# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=missing-function-docstring missing-module-docstring import-error

import pandas as pd
import pytest

from brioche import \
    BiomePftMatrix, TaxaPftMatrix, \
    BiomePftList, TaxaPftList, \
    Biomization, PollenCounts, \
    StabilizedPollenSamples, \
    BiomeAffinity

def test_join_matrix_mappings_into_biome_matrix():
    # taxa1: maps only through PFT 1 to biome 2
    # taxa2: maps only through PFT 2 to biome 1
    # taxa3: maps only to PFT 3, which doesn't map to any biome
    # taxa4: maps through PFT 2/4 to biome1 and PFT 1/4 to biome 2

    taxa_pfts = TaxaPftMatrix(pd.DataFrame.from_records(
            columns=('taxa', 1, 2, 3, 4),
            data=[
                ('taxa1', 1, 0, 1, 0),
                ('taxa2', 0, 1, 1, 0),
                ('taxa3', 0, 0, 1, 0),
                ('taxa4', 1, 1, 1, 1)
                ]))

    biome_pfts = BiomePftMatrix(pd.DataFrame.from_records(
            columns=('biome', 1, 2, 4),
            data=[
                ('biome1', 0, 1, 1),
                ('biome2', 1, 0, 1)
                ]))

    biomization = Biomization(taxa_pfts, biome_pfts)

    result = biomization.taxa_biome_matrix.to_dict()

    assert result == dict(
        biome1=dict(taxa1=0, taxa2=1, taxa4=1),
        biome2=dict(taxa1=1, taxa2=0, taxa4=1)
    )

def test_join_list_mappings_into_biome_matrix():
    # taxa1: maps only through PFT 1 to biome 2
    # taxa2: maps only through PFT 2 to biome 1
    # taxa3: maps only to PFT 3, which doesn't map to any biome
    # taxa4: maps through PFT 2/4 to biome1 and PFT 1/4 to biome 2

    taxa_pfts = TaxaPftList(pd.DataFrame.from_records(
            columns=('taxa', 'pft'),
            data=[
                ('taxa1', ['1', '3']),
                ('taxa2', ['2', '3']),
                ('taxa3', ['3']),
                ('taxa4', ['1', '2', '3', '4'])
                ]))

    biome_pfts = BiomePftList(pd.DataFrame.from_records(
            columns=('biome', 'pft'),
            data=[
                ('biome1', ['2', '4']),
                ('biome2', ['1', '4'])
                ]))

    biomization = Biomization(taxa_pfts, biome_pfts)

    result = biomization.taxa_biome_matrix.to_dict()

    assert result == dict(
        biome1=dict(taxa1=0, taxa2=1, taxa4=1),
        biome2=dict(taxa1=1, taxa2=0, taxa4=1)
    )

def test_get_biome_affinity():
    taxa_pfts = TaxaPftMatrix(pd.DataFrame.from_records(
            columns=('taxa', 1, 2, 3),
            data=[
                ('taxa1', 1, 1, 0),
                ('taxa2', 0, 1, 1),
                ('taxa3', 0, 0, 1),
                ('taxa4', 0, 0, 1)
                ]))

    # Use a 1-1 mapping between PFTs and biomes to simplify things
    biome_pfts = BiomePftMatrix(pd.DataFrame.from_records(
            columns=('biome', 1, 2, 3),
            data=[
                ('biome1', 1, 0, 0),
                ('biome2', 0, 1, 0),
                ('biome3', 0, 0, 1)
                ]))

    samples = StabilizedPollenSamples(
        samples=pd.DataFrame.from_dict(
            orient='index',
            columns=('taxa1', 'taxa2', 'taxa3', 'taxa4'),
            data=dict(
                taxa1_only_maps_to_biome1_as_least_specific=[
                    5, 0, 0, 0
                ],
                taxa2_only_maps_to_biome2_as_least_specific=[
                    0, 10, 0, 0
                ],
                taxa1_and_2_maps_to_biome2_as_highest_affinity=[
                    5, 10, 0, 0
                ],
                all_taxas_maps_to_biome3_as_highest_affinity=[
                    1, 2, 3, 4
                ],
                no_samples_maps_to_na=[
                    0, 0, 0, 0
                ]
            )),
        decimals=0,
        site="test")

    biomization = Biomization(taxa_pfts, biome_pfts)
    affinity = biomization.get_biome_affinity(samples)
    assert affinity.site == "test"

    biome_results = affinity.biomes.to_dict()
    assert biome_results == dict(
        taxa1_only_maps_to_biome1_as_least_specific='biome1',
        taxa2_only_maps_to_biome2_as_least_specific='biome2',
        taxa1_and_2_maps_to_biome2_as_highest_affinity='biome2',
        all_taxas_maps_to_biome3_as_highest_affinity='biome3',
        no_samples_maps_to_na='N/A'
    )

    score_results = affinity.scores.to_dict(orient='index')

    assert score_results == dict(
        taxa1_only_maps_to_biome1_as_least_specific=dict(
            biome1=pytest.approx(5),
            biome2=pytest.approx(5),
            biome3=pytest.approx(0)
        ),
        taxa2_only_maps_to_biome2_as_least_specific=dict(
            biome1=pytest.approx(0),
            biome2=pytest.approx(10),
            biome3=pytest.approx(10)
        ),
        taxa1_and_2_maps_to_biome2_as_highest_affinity=dict(
            biome1=pytest.approx(5),
            biome2=pytest.approx(15),
            biome3=pytest.approx(10)
        ),
        all_taxas_maps_to_biome3_as_highest_affinity=dict(
            biome1=pytest.approx(1),
            biome2=pytest.approx(3),
            biome3=pytest.approx(9)
        ),
        no_samples_maps_to_na=dict(
            biome1=pytest.approx(0),
            biome2=pytest.approx(0),
            biome3=pytest.approx(0)
        )
    )

def test_order_of_taxas_in_samples_does_not_matter():
    taxa_pfts = TaxaPftMatrix(pd.DataFrame.from_records(
            columns=('taxa', 1),
            data=[
                ('taxa1', 1),
                ('taxa2', 1),
                ('taxa3', 0),
                ]))

    biome_pfts = BiomePftMatrix(pd.DataFrame.from_records(
            columns=('biome', 1),
            data=[
                ('biome1', 1),
                ]))

    samples = StabilizedPollenSamples(
        samples=pd.DataFrame.from_dict(
            orient='index',
            columns=('taxa3', 'taxa2', 'taxa1'),
            data=dict(row=[4, 2, 1])),
        decimals=0,
        site="test")

    biomization = Biomization(taxa_pfts, biome_pfts)
    affinity = biomization.get_biome_affinity(samples)

    result = affinity.scores.loc['row', 'biome1']
    assert result == pytest.approx(3)


def test_ignore_unmapped_taxas():
    taxa_pfts = TaxaPftMatrix(pd.DataFrame.from_records(
            columns=('taxa', 1),
            data=[
                ('taxa1', 1),
                ('taxa2', 1),
                ('taxa3', 0),
                ]))

    biome_pfts = BiomePftMatrix(pd.DataFrame.from_records(
            columns=('biome', 1),
            data=[
                ('biome1', 1),
                ]))

    samples = StabilizedPollenSamples(
        samples=pd.DataFrame.from_dict(
            orient='index',
            columns=('taxa1', 'taxa2', 'taxa4'),
            data=dict(row=[4, 2, 1])),
        decimals=0,
        site="test")

    biomization = Biomization(taxa_pfts, biome_pfts)
    affinity = biomization.get_biome_affinity(samples)

    result = affinity.scores.loc['row', 'biome1']
    assert result == pytest.approx(6)


def test_get_unmapped_taxas():
    taxa_pfts = TaxaPftMatrix(pd.DataFrame.from_records(
            columns=('taxa', 1),
            data=[
                ('taxa1', 1),
                ('taxa2', 1),
                ]))

    biome_pfts = BiomePftMatrix(pd.DataFrame.from_records(
            columns=('biome', 1),
            data=[
                ('biome1', 1),
                ]))

    samples1 = PollenCounts(
        samples=pd.DataFrame.from_dict(
            orient='index',
            columns=('taxa1', 'taxa2', 'taxa3', 'taxa4'),
            data=dict(row=[1, 2, 3, 4])))

    samples2 = PollenCounts(
        samples=pd.DataFrame.from_dict(
            orient='index',
            columns=('taxa1', 'taxa2', 'taxa4', 'taxa5'),
            data=dict(row=[1, 2, 4, 5])))

    biomization = Biomization(taxa_pfts, biome_pfts)
    result = biomization.get_unmapped_taxas(samples1, samples2)

    assert result == {'taxa3', 'taxa4', 'taxa5'}

@pytest.mark.parametrize(('number_of_taxas', 'expected_score'), [
    (1, 0.01),
    (9, 0.09),
    (10, 0.010),
    (11, 0.011),
    (99, 0.099),
    (100, 0.0100),
    (191, 0.0191)
    ])
def test_tie_breaker_decrement_uses_enough_decimals_to_not_affect_affinity_score(number_of_taxas, expected_score):
    taxa_pfts = TaxaPftMatrix(pd.DataFrame.from_records(
            columns=('taxa', 1),
            data=[('taxa{}'.format(i), 1) for i in range(number_of_taxas)]))

    biome_pfts = BiomePftMatrix(pd.DataFrame.from_records(
            columns=('biome', 1),
            data=[
                ('biome1', 1),
                ]))

    samples = StabilizedPollenSamples(
        samples=pd.DataFrame.from_dict(
            orient='index',
            columns=('taxa0', ),
            data=dict(row=[1.1])),
        decimals=1)

    biomization = Biomization(taxa_pfts, biome_pfts)
    affinity = biomization.get_biome_affinity(samples)

    result = affinity._specificity_scores['biome1']
    assert result == pytest.approx(expected_score)


def test_apply_function_to_affinity_scores():
    affinity = BiomeAffinity(
        affinity_scores=pd.DataFrame.from_records(
            columns=('BiomeA', 'BiomeB'),
            data=[
                (5.0, 4.5),
                (5.0, 4.0),
            ]),
        specificity_scores=pd.Series(
            [0.02, 0.01],
            ['BiomeA', 'BiomeB']),
        decimals=1,
        site='test')

    assert list(affinity.biomes.values) == ['BiomeA', 'BiomeA']

    new_affinity = affinity.apply(lambda scores: scores.add(pd.Series(
            [0.04, 0.99],
            ['BiomeA', 'BiomeB'])))
    assert type(new_affinity) == BiomeAffinity

    result = new_affinity.scores.to_dict('records')
    assert result == [
        dict(BiomeA=pytest.approx(5.0), BiomeB=pytest.approx(5.5)),
        dict(BiomeA=pytest.approx(5.0), BiomeB=pytest.approx(5.0))
    ]

    assert list(new_affinity.biomes.values) == ['BiomeB', 'BiomeB']

    assert new_affinity.site == affinity.site
    assert new_affinity._decimals == affinity._decimals
    assert new_affinity._specificity_scores is affinity._specificity_scores
