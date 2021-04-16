# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=missing-function-docstring missing-module-docstring import-error

import pytest
import pandas as pd

from brioche.tool import main

SEPS = pytest.mark.parametrize('sep', [',', ';'])

@SEPS
def test_pollen_counts_for_multiple_sites(tmp_path, sep):
    taxas = write_taxas(tmp_path, sep)
    biomes = write_biomes(tmp_path, sep)

    site1 = write_samples(tmp_path, 'site1', sep,
        ('depth', 'taxa1', 'taxa2', 'taxa3'),
        (10, 1, 4, 45))

    site2 = write_samples(tmp_path, 'site2', sep,
        ('depth', 'taxa1', 'taxa0'),
        (20, 1, 9))

    main(['--decimals=1', 
        '--separator', sep,
        '--save-percentages', 
        '--save-stabilized',
        '--taxas', taxas,
        '--biomes', biomes,
        site1, site2])

    assert read_csv(tmp_path / 'site1_percentages.csv') == expected_csv(sep,
        ('depth', 'taxa1', 'taxa2', 'taxa3'),
        (10, '2.0', '8.0', '90.0'))

    assert read_csv(tmp_path / 'site1_stabilized.csv') == expected_csv(sep,
        ('depth', 'taxa1', 'taxa2', 'taxa3'),
        (10, '1.2', '2.7', '9.5'))

    assert read_csv(tmp_path / 'site1_scores.csv') == expected_csv(sep,
        ('depth', 'biome1', 'biome2', 'biome3'),
        (10, '1.2', '2.7', '9.5'))

    assert read_csv(tmp_path / 'site1_biomes.csv') == expected_csv(sep,
        ('depth', 'Biome'),
        (10, 'biome3'))

    assert read_csv(tmp_path / 'site2_percentages.csv') == expected_csv(sep,
        ('depth', 'taxa1', 'taxa0'),
        (20, '10.0', '90.0'))

    assert read_csv(tmp_path / 'site2_stabilized.csv') == expected_csv(sep,
        ('depth', 'taxa1', 'taxa0'),
        (20, '3.1', '9.5'))

    assert read_csv(tmp_path / 'site2_scores.csv') == expected_csv(sep,
        ('depth', 'biome1', 'biome2', 'biome3'),
        (20, '12.6', '9.5', '9.5'))

    assert read_csv(tmp_path / 'site2_biomes.csv') == expected_csv(sep,
        ('depth', 'Biome'),
        (20, 'biome1'))

@SEPS
def test_pollen_percentages_with_high_default_threshold(tmp_path, sep):
    taxas = write_taxas(tmp_path, sep)
    biomes = write_biomes(tmp_path, sep)

    site1 = write_samples(tmp_path, 'site1', sep,
        ('depth', 'taxa1', 'taxa2', 'taxa3'),
        (10, 1, 9, 90),
        (20, 50, 40, 10))

    main(['--decimals=3', 
        '--separator', sep,
        '--default-threshold=10.5',
        '--save-stabilized',
        '--type=percentages',
        '--taxas', taxas,
        '--biomes', biomes,
        site1])

    assert read_csv(tmp_path / 'site1_stabilized.csv') == expected_csv(sep,
        ('depth', 'taxa1', 'taxa2', 'taxa3'),
        (10, '0.000', '0.000', '8.916'),
        (20, '6.285', '5.431', '0.000'))

    assert read_csv(tmp_path / 'site1_scores.csv') == expected_csv(sep,
        ('depth', 'biome1', 'biome2', 'biome3'),
        (10, '0.000', '0.000', '8.916'),
        (20, '6.285', '5.431', '0.000'))

    assert read_csv(tmp_path / 'site1_biomes.csv') == expected_csv(sep,
        ('depth', 'Biome'),
        (10, 'biome3'),
        (20, 'biome1'))


@SEPS
def test_stabilzed_pollen_samples(tmp_path, sep):
    taxas = write_taxas(tmp_path, sep)
    biomes = write_biomes(tmp_path, sep)

    site1 = write_samples(tmp_path, 'site1', sep,
        ('depth', 'taxa0', 'taxa2', 'taxa3'),
        (10, '1.10', '3.33', '0.00'))

    main(['--separator', sep,
        '--type=stabilized',
        '--taxas', taxas,
        '--biomes', biomes,
        site1])

    assert read_csv(tmp_path / 'site1_scores.csv') == expected_csv(sep,
        ('depth', 'biome1', 'biome2', 'biome3'),
        (10, '1.10', '4.43', '1.10'))

    assert read_csv(tmp_path / 'site1_biomes.csv') == expected_csv(sep,
        ('depth', 'Biome'),
        (10, 'biome2'))


# Simple taxa mapping: taxa1/2/3 maps to PFTs 1/2/3 respectively
# Also include taxa0 that maps to PFTs 1,2,3 to check that irregular CSV files work
def write_taxas(tmp_path, sep):
    taxa_file = tmp_path / 'taxas.csv'

    with open(taxa_file, 'wt') as f:
        f.write(f'taxa0{sep}1{sep}2{sep}3\n')
        for i in range(1,4):
            f.write(f'taxa{i}{sep}{i}\n')

    return str(taxa_file)

# Simple mapping: biome1/2/3 maps to PFTs 1/2/3 respectively
def write_biomes(tmp_path, sep):
    biome_file = tmp_path / 'biomes.csv'

    with open(biome_file, 'wt') as f:
        for i in range(1,4):
            f.write(f'biome{i}{sep}{i}\n')

    return str(biome_file)

def write_samples(tmp_path, site, sep, *rows):
    sample_file = tmp_path / f'{site}.csv'

    with open(sample_file, 'wt') as f:
        for row in rows:
            f.write(sep.join(map(str, row)))
            f.write('\n')

    return str(sample_file)

def read_csv(path):
    with open(path, 'rt') as f:
        return f.read()

def expected_csv(sep, *rows):
    return '\n'.join([sep.join(map(str, row)) for row in rows]) + '\n'