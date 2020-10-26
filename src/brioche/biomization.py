
class Biomization:
    def __init__(self, pft_taxas, pft_biomes):
        # Join the mappings on PFTs to get relationships between taxas and biomes
        self.taxa_biome_mapping = pft_biomes.mapping.merge(
            pft_taxas.mapping, left_on=pft_biomes.pft_key, right_on=pft_taxas.pft_key, how='outer'
            ).assign(taxa_in_biome=lambda row: row.taxa_in_pft * row.biome_has_pft)

        # Turn the relationships back into a matrix indexed by taxa with one column per biome
        self.taxa_biome_matrix = self.taxa_biome_mapping.pivot_table(
            index='taxa', columns='biome', values='taxa_in_biome',
            aggfunc=lambda v: int(any(v)), fill_value=0)
