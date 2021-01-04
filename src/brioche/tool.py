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
parser.add_argument('--separator', '-s', default=',', help='Column separator')
parser.add_argument('--decimals', type=int, choices=range(5), default=2, help='Decimals to use in stabilized sample values')
parser.add_argument('--default-threshold', '-d', type=float, default=0.5, help='Default percentage threshold')
parser.add_argument('--type', choices=['counts', 'percentages', 'stabilized'], 
    default='counts', help='Type of values in the pollen sample files')
parser.add_argument('--taxas', '-t', required=True, help='Taxa to PFT mapping CSV file')
parser.add_argument('--biomes', '-b', required=True, help='Biome to PFT mapping CSV file')
parser.add_argument('samples', nargs='+', help='Pollen sample CSV files')

def main():
    args = parser.parse_args()
    taxas = TaxaPftList.read_csv(args.taxas)
    biomes = BiomePftList.read_csv(args.biomes)
    samples = list(read_samples(args))

    biomization = Biomization(taxas, biomes)

    unmapped = biomization.get_unmapped_taxas(*samples)
    if unmapped:
        print('Warning: sample files contain taxas that are not mapped to any biome:')
        for t in unmapped:
            print(t)
        print()

    for sample in samples:
        print('Reading samples:', sample.site)

        biomes_path = '{}_biomes.csv'.format(sample.site)
        scores_path = '{}_scores.csv'.format(sample.site)

        affinity = biomization.get_biome_affinity(sample.get_stabilized(default_threshold=args.default_threshold, decimals=args.decimals))
        affinity.biomes_to_csv(biomes_path, sep=args.separator)
        affinity.scores_to_csv(scores_path, sep=args.separator)

        print('Wrote biomes to:', biomes_path)
        print('Wrote scores to:', scores_path)
        print()


def read_samples(args):
    for sample in args.samples:
        base = os.path.splitext(sample)[0]

        if args.type == 'counts':
            yield PollenCounts.read_csv(sample, site=base, sep=args.separator)

        elif args.type == 'percentages':
            yield PollenPercentages.read_csv(sample, site=base, sep=args.separator)

        elif args.type == 'stabilized':
            yield StabilizedPollenSamples.read_csv(sample, decimals=args.decimals, site=base, sep=args.separator)
