# brioche

[![PyPI version](https://badge.fury.io/py/brioche.svg)](https://badge.fury.io/py/brioche)
[![DOI](https://zenodo.org/badge/305771587.svg)](https://doi.org/10.5281/zenodo.14207034)

Brioche is a Python library for performing a biomization analysis of pollen samples.

It implements the protocol defined by Prentice et al. (1996), using Pandas for efficient analysis of a large number of pollen samples across time or sites. It was implemented to support a study of eastern African mountain evolution by Githumbi et al. (submitted).

Brioche is best used in a Jupyter notebook, but the library also includes a command line tool.

# Method

To use Brioche you need to define a set of plant functional types (PFTs). As defined by Prentice et al., PFTs are "broad classes of plant defined by stature (e.g. tree/shrub), leaf form (e.g. broad-leaved/needle-leaved), phenology (e.g. evergreen/deciduous), and climatic adaptations". In brioche each PFT is identified by a number:

TODO: example table.

Next you need to define a **biome x PFT matrix** that maps your set of biomes to the PFTs that are dominant in each one.  Working with a full matrix can be unwieldy, so brioche supports reading a simple table with one row for each biome, followed by a list of the PFTs that map to it:

| Biome | PFTs |
|-------|------|
| Grassland/afroalpine | 12 |
| Ericaceous scrub | 17 9 14 12 |
| Moorland | 13 14 15 |	

Finally the taxa in the samples must be mapped to one or more PFTs in a **taxa x PFT matrix**. (Prentice uses a *PFT x taxon matrix* instead, but the transposed structure is easier to work with since there's typically many more taxa than PFTs.) This is also most conveniently represented as a table with one row for each taxon, followed by a list of the PFTs that it maps to:

| Taxa | PFTs |
|------|------|
| Abrus | 7 10 |
| Abutilon | 1 7 |
| Acacia | 2 4 6 7 |
| Acalypha | 10 11 |	

Brioche combines the two mappings to create a **taxon x biome matrix** (again, Prentice uses a *biome x taxon matrix*), where each cell holds a 1 or a 0 to indicate if the taxon maps to that biome.  This matrix is only used during the calculation, but can be output to verify the mapping.

TODO: reading samples, producing output


# References

Githumbi et al., submitted. Understanding Eastern African Montane Forest Evolution since the end of the Last Glacial Maxima.

Prentice, C., Guiot, J., Huntley, B., Jolly, D., Cheddadi, R., 1996. Reconstructing biomes from palaeoecological data: a general method and its application to European pollen data at 0 and 6 ka. Clim. Dyn. 12, 185–194.
