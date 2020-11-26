# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=missing-function-docstring missing-module-docstring import-error

import pandas as pd

from brioche import BiomePftMapping, TaxaPftMapping, Biomization

def test_join_mappings_into_biome_matrix():
    # taxa1: maps only through PFT 1 to biome 2
    # taxa2: maps only through PFT 2 to biome 1
    # taxa3: maps only to PFT 3, which doesn't map to any biome
    # taxa4: maps through PFT 2/4 to biome1 and PFT 1/4 to biome 2

    taxa_pfts = TaxaPftMapping(pd.DataFrame.from_records(
            columns=('taxa', 1, 2, 3, 4),
            data=[
                ('taxa1', 1, 0, 1, 0),
                ('taxa2', 0, 1, 1, 0),
                ('taxa3', 0, 0, 1, 0),
                ('taxa4', 1, 1, 1, 1)
                ]))

    biome_pfts = BiomePftMapping(pd.DataFrame.from_records(
            columns=('biome', 1, 2, 4),
            data=[
                ('biome1', 0, 1, 1),
                ('biome2', 1, 0, 1)
                ]))

    biomization = Biomization(taxa_pfts, biome_pfts)

    result = biomization.taxa_biome_matrix.to_dict()

    assert result == dict(
        biome1=dict(taxa1=0, taxa2=1, taxa3=0, taxa4=1),
        biome2=dict(taxa1=1, taxa2=0, taxa3=0, taxa4=1)
    )
