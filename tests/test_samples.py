# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=missing-function-docstring missing-module-docstring import-error

import pytest
import pandas as pd

from brioche import PollenCounts, PollenPercentages

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
        ]),
        site="test")

    percentages = counts.get_percentages()
    result = percentages.samples.to_dict('records')

    assert result == [
        dict(TaxaA=25.0, TaxaB=0, TaxaC=75.0),
        dict(TaxaA=10.0, TaxaB=20.0, TaxaC=70.0),
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
