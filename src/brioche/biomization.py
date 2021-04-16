# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=import-error

import math
import pandas as pd

class Biomization:
    def __init__(self, pft_taxas, pft_biomes):
        # Join the mappings on PFTs to get relationships between taxas and biomes
        self._taxa_biome_mapping = pft_biomes.mapping.merge(
            pft_taxas.mapping, on='pft', how='outer', sort=False)

        # Turn the relationships back into a matrix indexed by taxa with one column per biome
        self._taxa_biome_matrix = self._taxa_biome_mapping.pivot_table(
            index='taxa', columns='biome', values='pft',
            aggfunc=lambda v: 1,
            fill_value=0)

        # Count the mapped taxas per biome to calculate specificity adjustments below
        self._taxas_per_biome = self._taxa_biome_matrix.sum(axis='index')
        self._specificity_decimals = int(math.log10(self._taxas_per_biome.max())) + 1

    @property
    def taxa_biome_mapping(self): return self._taxa_biome_mapping

    @property
    def taxa_biome_matrix(self): return self._taxa_biome_matrix

    def get_unmapped_taxas(self, *sites):
        return {
            taxa
            for site in sites
            for taxa in site.samples
            if taxa not in self._taxa_biome_matrix.index
        }

    def get_biome_affinity(self, stabilized_samples):
        samples = stabilized_samples.samples

        # Build up a data frame for the affinity scores by starting
        # with an empty one using the same index as the samples
        # (which is probably sample depth), then calculate an 
        # affinity score for each biome.
        affinity_scores = pd.DataFrame(index=samples.index)

        # Calculate an affinity score for the biome by multiplying the stablized sample values
        # with the 1s and 0s from the mapping, i.e. filtering out taxas that aren't mapped
        # and summing the remaining ones.  
        for biome in self._taxa_biome_matrix:
            affinity_scores[biome] = samples.mul(self._taxa_biome_matrix[biome], axis='columns').sum(axis='columns')

        # Also calculate a specificity score for the biomes, which will be deducted 
        # from the affinity scores as a tie-breaker in favour of the least specific
        # biome.  This is expressed as a fractional number below the number of decimals 
        # used in the samples.
        decimals = stabilized_samples.decimals + self._specificity_decimals
        specificity_scores = pd.Series([self._taxas_per_biome[biome] * 10 ** -decimals
                                        for biome in self._taxa_biome_matrix],
                                        index=self._taxa_biome_matrix.columns)

        return BiomeAffinity(affinity_scores, specificity_scores, stabilized_samples.site, stabilized_samples.decimals)

class BiomeAffinity:
    def __init__(self, affinity_scores, specificity_scores, site, decimals):
        self._affinity_scores = affinity_scores
        self._specificity_scores = specificity_scores
        self._site = site
        self._decimals = decimals

        # Deduct the specificity scores to give biomes with more mapped taxas a slightly
        # lower score than the ones with fewer, to break any ties between them.
        scores = affinity_scores.sub(specificity_scores)

        # For each row find the column with the highest value, i.e. the biome with the highest affinity score
        self._biomes = scores.idxmax(axis='columns')
        self._biomes.name = 'Biome'

        # Remove rows where there are no values
        score_sums = affinity_scores.sum(axis=1)
        self._biomes[score_sums == 0] = 'N/A'

    @property
    def biomes(self): return self._biomes

    @property
    def scores(self): return self._affinity_scores

    @property
    def site(self): return self._site

    def apply(self, score_func):
        new_scores = score_func(self._affinity_scores).round(self._decimals)
        return BiomeAffinity(new_scores, self._specificity_scores, self._site, self._decimals)

    def biomes_to_csv(self, path_or_buf, **kwargs):
        self.biomes.to_csv(path_or_buf, **kwargs)

    def scores_to_csv(self, path_or_buf, **kwargs):
        self.scores.to_csv(path_or_buf, float_format='%.{}f'.format(self._decimals), **kwargs)
