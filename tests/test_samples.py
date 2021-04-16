# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=missing-function-docstring missing-module-docstring import-error

import pytest
import pandas as pd

from brioche import PollenCounts, PollenPercentages, StabilizedPollenSamples

def test_get_taxas():
    counts = PollenCounts(pd.DataFrame.from_records(
        columns=('Taxa A', 'Taxa B', 'Taxa C'),
        data=[(1, 0, 1)]))

    assert list(counts.taxas) == ['Taxa A', 'Taxa B', 'Taxa C']

def test_calculate_percentages_from_counts():
    counts = PollenCounts(pd.DataFrame.from_records(
        columns=('TaxaA', 'TaxaB', 'TaxaC'),
        data=[
            (5, 0, 15),
            (1, 2, 7),
            (0, 0, 0)
        ]),
        site="test")

    percentages = counts.get_percentages()
    result = percentages.samples.to_dict('records')

    assert result == [
        dict(TaxaA=25.0, TaxaB=0, TaxaC=75.0),
        dict(TaxaA=10.0, TaxaB=20.0, TaxaC=70.0),
        dict(TaxaA=0.0, TaxaB=0.0, TaxaC=0.0),
    ]

    assert counts.site == percentages.site


@pytest.mark.parametrize(('decimals', 'expected_value'), [
    (None, 100 / 6.0),
    (0, 17.0),
    (1, 16.7),
    (2, 16.67)])
def test_calculate_rounded_percentages_from_counts(decimals, expected_value):
    counts = PollenCounts(pd.DataFrame.from_records(
        columns=('TaxaA', 'TaxaB'),
        data=[
            (1, 5)
        ]))

    percentages = counts.get_percentages(decimals=decimals)
    result = percentages.samples.iat[0, 0]

    assert result == pytest.approx(expected_value)


@pytest.mark.parametrize(('decimals', 'expected_value'), [
    (None, 100 / 6.0),
    (0, 17.0),
    (1, 16.7),
    (2, 16.67)])
def test_get_rounded_percentages(decimals, expected_value):
    percentages = PollenPercentages(pd.DataFrame.from_records(
        columns=('TaxaA', ),
        data=[
            (100 / 6.0, )
        ]))

    rounded = percentages.get_percentages(decimals=decimals)
    result = rounded.samples.iat[0, 0]

    assert result == pytest.approx(expected_value)
    assert rounded.site == percentages.site


def test_get_percentages_without_rounding_returns_the_same_object():
    percentages = PollenPercentages(pd.DataFrame.from_records(
        columns=('TaxaA', ),
        data=[
            (100 / 6.0, )
        ]))

    result = percentages.get_percentages()

    assert result is percentages


@pytest.mark.parametrize(('percentage', 'threshold', 'decimals', 'expected'), [
    (25.5, 0.5, 2, 5.0),
    (1.1, 1.0, 2, 0.32),
    (1.1, 1.0, 3, 0.316),
    (1.0, 1.0, 5, 0.0),
    (0.1, 0.1, 5, 0.0),
    ])
def test_get_stabilized_using_default_threshold(percentage, threshold, decimals, expected):
    percentages = PollenPercentages(pd.DataFrame.from_records(
        columns=('TaxaA', ),
        data=[
            (percentage, )
        ]))

    stabilized = percentages.get_stabilized(default_threshold=threshold, decimals=decimals)
    result = stabilized.samples.iat[0, 0]

    assert result == pytest.approx(expected)


class DummyWorksheet:
    def __init__(self, title, *rows):
        self.title = title
        self._values = rows

    def get_all_values(self, value_render_option): 
        return self._values

def test_read_counts_from_google_sheet():
    counts = PollenCounts.read_google_sheet(DummyWorksheet('test',
        ('Level', 'foo', 'bar'),
        ('a', 14, ''),
        ('b', '', 13.2)
    ))

    result = counts.samples.to_dict('index')

    assert counts.site == 'test'
    assert result == dict(
        a=dict(foo=14, bar=0),
        b=dict(foo=0, bar=13)
    )

def test_read_percentages_from_google_sheet():
    percentages = PollenPercentages.read_google_sheet(DummyWorksheet('test',
        ('Level', 'foo', 'bar'),
        ('a', 14, ''),
        ('b', '', 13.2)
    ))

    result = percentages.samples.to_dict('index')

    assert percentages.site == 'test'
    assert result == dict(
        a=dict(foo=pytest.approx(14.0), bar=0),
        b=dict(foo=0, bar=pytest.approx(13.2))
    )

def test_read_stabilized_from_google_sheet():
    stabilized = StabilizedPollenSamples.read_google_sheet(DummyWorksheet('test',
        ('Level', 'foo', 'bar'),
        ('a', 14, ''),
        ('b', '', 13.2)
    ), decimals=4)

    result = stabilized.samples.to_dict('index')

    assert stabilized.site == 'test'
    assert stabilized.decimals == 4
    assert result == dict(
        a=dict(foo=pytest.approx(14.0), bar=0),
        b=dict(foo=0, bar=pytest.approx(13.2))
    )

def test_raise_exception_for_duplicate_columns_in_google_sheet():
    with pytest.raises(ValueError, match=r'^Duplicate columns in test: .*foo'):
        PollenCounts.read_google_sheet(DummyWorksheet('test',
            ('Depth', 'foo', 'bar', 'foo'),
            (10, 14, 0, 0),
        ))

def test_read_multi_index_counts_from_google_sheet():
    counts = PollenCounts.read_google_sheet(DummyWorksheet('test',
        ('Depth', 'foo', 'Age', 'bar'),
        (100, 14, 158, ''),
        (200, '', 354, 13.2)
    ), index_col=[0, 2])

    result = counts.samples.to_dict('index')

    assert result == {
        (100, 158): dict(foo=14, bar=0),
        (200, 354): dict(foo=0, bar=13)
    }


def test_apply_function_to_counts():
    counts = PollenCounts(pd.DataFrame.from_records(
        columns=('TaxaA', 'TaxaB'),
        data=[
            (5, 15),
            (1, 0),
            (3, 7),
        ]),
        site="test")

    new_counts = counts.apply(lambda samples: samples[samples['TaxaB'] != 0])
    assert type(new_counts) == PollenCounts

    result = new_counts.samples.to_dict('records')
    assert result == [
        dict(TaxaA=5, TaxaB=15),
        dict(TaxaA=3, TaxaB=7),
    ]

    assert new_counts.site == counts.site

def test_apply_function_to_percentages():
    percentages = PollenPercentages(pd.DataFrame.from_records(
        columns=('TaxaA', 'TaxaB'),
        data=[
            (5, 15),
            (1, 0),
            (3, 7),
        ]),
        site="test")

    new_percentages = percentages.apply(lambda samples: samples[samples['TaxaB'] != 0])
    assert type(new_percentages) == PollenPercentages

    result = new_percentages.samples.to_dict('records')
    assert result == [
        dict(TaxaA=5, TaxaB=15),
        dict(TaxaA=3, TaxaB=7),
    ]

    assert new_percentages.site == percentages.site

def test_apply_function_to_stabilized_samples():
    stab = StabilizedPollenSamples(pd.DataFrame.from_records(
        columns=('TaxaA', 'TaxaB'),
        data=[
            (5, 15),
            (1, 0),
            (3, 7),
        ]),
        decimals=1,
        site="test")

    new_stab = stab.apply(lambda samples: samples[samples['TaxaB'] != 0])
    assert type(new_stab) == StabilizedPollenSamples

    result = new_stab.samples.to_dict('records')
    assert result == [
        dict(TaxaA=5, TaxaB=15),
        dict(TaxaA=3, TaxaB=7),
    ]

    assert new_stab.site == stab.site
    assert new_stab.decimals == stab.decimals
