# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

"""Command line tool to run brioche on CSV files.
"""

import os
import argparse

from . import __version__
from .mappings import BiomePftList, TaxaPftList
from .samples import PollenCounts, PollenPercentages, StabilizedPollenSamples
from .biomization import Biomization

parser = argparse.ArgumentParser(description='Perform biome affinity analysis of pollen samples')
parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
parser.add_argument('--separator', '-s', default=',', help='Column separator (default comma)', metavar='CHAR/REGEXP')
parser.add_argument('--decimals', type=int, choices=range(5), default=2, help='Decimals to use in stabilized sample values (default 2)')
parser.add_argument('--default-threshold', '-d', type=float, default=0.5, help='Default sample stabilization threshold (default 0.5)', metavar='THRESHOLD')
parser.add_argument('--type', choices=['counts', 'percentages', 'stabilized'], 
    default='counts', help='Type of values in the pollen sample files (default counts)')
parser.add_argument('--save-percentages', action='store_true', help='Save calculated sample percentages')
parser.add_argument('--save-stabilized', action='store_true', help='Save calculated stabilized sample values')
parser.add_argument('--taxas', '-t', required=True, help='Taxa to PFT mapping CSV file', metavar='TAXAS.CSV')
parser.add_argument('--biomes', '-b', required=True, help='Biome to PFT mapping CSV file', metavar='BIOMES.CSV')
parser.add_argument('--index', type=int, action='append', help='Index column, counting from 0 (repeat option if there are multiple index columns). If omitted the first column is used')
parser.add_argument('samples', nargs='+', help='Pollen sample CSV files', metavar='SAMPLE.CSV')

def main(cli_args=None):
    args = parser.parse_args(cli_args)
    taxas = TaxaPftList.read_csv(args.taxas, sep=args.separator)
    biomes = BiomePftList.read_csv(args.biomes, sep=args.separator)
    samples = list(read_samples(args))

    biomization = Biomization(taxas, biomes)

    unmapped = biomization.get_unmapped_taxas(*samples)
    if unmapped:
        print('Warning: sample files contain taxas that are not mapped to any biome:')
        for t in unmapped:
            print(t)
        print()

    for sample in samples:
        print('Reading samples from:', sample.site)

        base = os.path.splitext(sample.site)[0]

        biomes_path = '{}_biomes.csv'.format(base)
        scores_path = '{}_scores.csv'.format(base)

        stabilized = sample.get_stabilized(default_threshold=args.default_threshold, decimals=args.decimals)

        if args.save_percentages:
            percentages_path = '{}_percentages.csv'.format(base)
            sample.get_percentages(args.decimals).to_csv(percentages_path, decimals=args.decimals, sep=args.separator)
            print('Wrote percentages to:', percentages_path)

        if args.save_stabilized:
            stabilized_path = '{}_stabilized.csv'.format(base)
            stabilized.to_csv(stabilized_path, sep=args.separator)
            print('Wrote stabilized to: ', stabilized_path)

        affinity = biomization.get_biome_affinity(stabilized)
        affinity.biomes_to_csv(biomes_path, sep=args.separator)
        affinity.scores_to_csv(scores_path, sep=args.separator)

        print('Wrote biomes to:     ', biomes_path)
        print('Wrote scores to:     ', scores_path)
        print()


def read_samples(args):
    index_col = args.index or [0]

    for sample in args.samples:
        if args.type == 'counts':
            yield PollenCounts.read_csv(sample, site=sample, index_col=index_col, sep=args.separator)

        elif args.type == 'percentages':
            yield PollenPercentages.read_csv(sample, site=sample, index_col=index_col, sep=args.separator)

        elif args.type == 'stabilized':
            yield StabilizedPollenSamples.read_csv(sample, decimals=args.decimals, site=sample, index_col=index_col, sep=args.separator)
