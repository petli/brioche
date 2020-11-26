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

def test_calculate_percentages():
    counts = PollenCounts(pd.DataFrame.from_records(
        columns=('TaxaA', 'TaxaB', 'TaxaC'),
        data=[
            (5, 0, 15),
            (1, 2, 7),
        ]))

    percentages = counts.get_percentages()

    result = percentages.samples.to_dict('records')

    assert result == [
        dict(TaxaA=25.0, TaxaB=0, TaxaC=75.0),
        dict(TaxaA=10.0, TaxaB=20.0, TaxaC=70.0),
    ]
