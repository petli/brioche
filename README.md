# brioche

[![PyPI version](https://badge.fury.io/py/brioche.svg)](https://badge.fury.io/py/brioche)
[![DOI](https://zenodo.org/badge/305771587.svg)](https://doi.org/10.5281/zenodo.14207034)

Brioche is a Python library for performing a biomization analysis of pollen samples.

It implements the protocol defined by Prentice et al. (1996), using Pandas for efficient analysis of a large number of pollen samples across time or sites. It was implemented to support a study of eastern African mountain evolution by Githumbi et al. (submitted).

Brioche is best used in a Jupyter notebook, but the library also includes a command line tool.

The following sections describe the biomisation protocol as implemented in Brioche at an overview level. The [example Jupyter notebook](examples/biomization.ipynb) shows how to use the library to process pollen samples from Excel files, and can be used both as documentation and as a starting point for your own analysis.

# Mapping biomes

To use Brioche you need to define a set of plant functional types (PFTs). As defined by Prentice et al., PFTs are "broad classes of plant defined by stature (e.g. tree/shrub), leaf form (e.g. broad-leaved/needle-leaved), phenology (e.g. evergreen/deciduous), and climatic adaptations". In brioche each PFT is identified by a number. These are the PFTs defined for the analysis in Githumbi et al. (submitted):

| PFT |	Description |
|-----|-------------|
| 1 |	Wet temperate evergreen tree (<15c, >1200mmyr-1)
| 2	| Dry temperate evergreen tree (<15c, <1200mmyr-1)
| 3	| Wet tropical evergreen tree(>15c, >1200mmyr-1)
| 4	| Dry tropical evergreen tree(>15c, <1200mmyr-1)
| 5	| Wet tropical raingreen tree (>1200mmyr-1)
| 6	| Dry tropical raingreen tree
| 7	| Tropical woody shrub
| 8	| Temperate woody shrub
| 9	| Frost tolerant woody shrub/tree
| 10 | Tropical herb/forb
| 11 | Temperate herb/forb
| 12 | Frost tolerant herb/forb
| 13 | Temperate sclerophyllous
| 14 | Grass
| 15 | Wetland taxa (sedges/herbs)
| 16 | Fire tolerant temperate tree/shrub
| 17 | Fire tolerant tropical tree/shrub
| 18 | Succulent woody shrub/tree
| 19 | Liana
| 20 | Fern
| 21 | Palm

Next you need to define a **biome x PFT matrix** that maps your set of biomes to the PFTs that are dominant in each one.  Working with a full matrix can be unwieldy, so brioche supports reading a simple table with one row for each biome, followed by a list of the PFTs that map to it:

| Biome | PFTs |
|-------|------|
| Grassland/afroalpine | 12 |
| Ericaceous scrub | 17 9 14 12 |
| Moorland | 13 14 15 |	

Finally the taxa in the samples must be mapped to one or more PFTs in a **taxon x PFT matrix**. (Prentice uses a *PFT x taxon matrix* instead, but the transposed structure is easier to work with since there's typically many more taxa than PFTs.) This is also most conveniently represented as a table with one row for each taxon, followed by a list of the PFTs that it maps to:

| Taxa | PFTs |
|------|------|
| Abrus | 7 10 |
| Abutilon | 1 7 |
| Acacia | 2 4 6 7 |
| Acalypha | 10 11 |	

Brioche combines the two mappings to create a **taxon x biome matrix** (again, Prentice uses a *biome x taxon matrix*), where each cell holds a 1 or a 0 to indicate if the taxon maps to that biome.  This matrix is only used during the calculation, but can be output to verify the mapping.

The matrixes are represented as unpivoted lists in Brioche using the classes `BiomePftList` and `TaxaPftList`. They are best constructed with the class methods `read_csv()`, `read_excel_sheet()` and `read_google_sheet()`.

Alternatively, if you prefer to work with a matrix where you map taxa and biomes to PFTs by entering 1 and 0 in each cell you can use the classes `BiomePftMatrix` and `TaxaPftMatrix`.  Parts of the biome x PFT mapping above would then look like this:

| Biome                 | 12 | 13 | 14 | 15 |
|-----------------------|----|----|----|----|
| Grassland/afroalpine  |  1 |  0 |  0 |  0 |
| Ericaceous scrub      |  1 |  0 |  1 |  0 |
| Moorland              |  0 |  1 |  1 |  1 |


# Reading pollen samples

The classes `PollenCounts` and `PollenPercentages` (which both implement the abstract base class `PollenSamples`) hold pollen samples for the analysis as absolute number or percentages, respectively.  They can be loaded using the class methods `read_csv()` or `read_google_sheet()`, while Excel files are easiest to load the Pandas utility function `pd.read_excel()` and instantiating the classes from the resulting data frames directly (see the example notebook).

The source must have at least one index column that typically represent sample depth or age. It is also  ossible with compound keys where the sample data contains both depth and age. There should be one column per taxon. Partial example:

| Depth	| Age | Cyperaceae | Poaceae | Helichrysum
|-------|-----|------------|---------|-------------
| 703 | 3329 | 102 | 103 | 11
| 753 | 3445 | 106 | 88 | 11
| 803 | 3562 | 99 | 70 | 8


# Biome affinity analysis

The analysis is performed by instantiating the class `Biomization` providing the `TaxaPftList` and `BiomePftList` objects from above. To make it easier to build up the mapping the method `get_unmapped_taxas()` provide a list of taxa that are not mapped to any biome, either because they are not mapped to any PFT or because a PFT is not mapped to any biome.

The analysis is performed on stabilized sample values, which are calculated as the square root of the percentages to reduce the impact of dominant taxa.  A threshold can be subtracted from the percentages before the square root is calculated, setting any negative numbers to 0, to ignore taxa with very low numbers from the analysis.

`PollenCounts` and `PollenPercentages` provide the `get_stabilized()` method which returns a `StabilizedPollenSamples` object.  This is passed to `Biomization.get_biome_affinity()` method which returns a `BiomeAffinity` result object.  The results are provided by two properties:

* `scores`: A `pd.DataFrame` with the calculated affinity scores for each biome for each sample. The score for one biome is calculated by adding the stabilized values for each taxa that are mapped to that biome via the PFTs.
* `biomes`: a `pd.Series` containing the name of the biome with the highest affinity score for each sample. In case of ties, the biome with the fewest mapped taxa will be chosen. The logic from Prentice is that biomes with more mapped taxa are identified by the presence of those additional taxa, and in their absence they should not be selected over a biome that does not include them.

For a complete example, see the example notebook. This has the additional step of explicitly calculating pollen percentages to a specific number of decimals, rather than going directly from pollen counts to stabilized values.  


# Extending the Brioche analysis

The classes `PollenCounts`, `PollenPercentages`, `StabilizedPollenSamples` and `BiomeAffinity` all have an `apply()` method that allows the underlying dataframe to be processed by any Pandas code, and returns a new object containing the results.  The example notebook demonstrates how to use this to bin affinity scores on age.


# Processing the result

The `BiomeAffinity` properties can be written to Excel files for further processing, be further processed in Python using Pandas or plotted.  Again, see the example notebook.


# References

Githumbi et al., submitted. Understanding Eastern African Montane Forest Evolution since the end of the Last Glacial Maxima.

Prentice, C., Guiot, J., Huntley, B., Jolly, D., Cheddadi, R., 1996. Reconstructing biomes from palaeoecological data: a general method and its application to European pollen data at 0 and 6 ka. Clim. Dyn. 12, 185–194.
