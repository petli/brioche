# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=import-error

import numpy as np

class PollenSamples:
    def __init__(self, samples, site=None):
        self._samples = samples
        self._site = site

    @property
    def samples(self): return self._samples

    @property
    def taxas(self): return self._samples.columns
        
    @property
    def site(self): return self._site

    def get_percentages(self, decimals=None): 
        raise NotImplementedError()

    def get_stabilized(self, default_threshold=0.0, decimals=2):
        percentages = self.get_percentages()

        # TODO: support per-taxa thresholds
        stabilized = (percentages.samples
                        .sub(default_threshold)
                        .clip(lower=0)
                        .apply(np.sqrt)
                        .round(decimals))

        return StabilizedPollenSamples(stabilized, site=self.site, decimals=decimals)


class PollenCounts(PollenSamples):
    def get_percentages(self, decimals=None): 
        sums = self.samples.sum(axis=1)
        percentages = self.samples.apply(lambda column: column * 100 / sums)

        if decimals is not None:
            percentages = percentages.round(decimals)

        return PollenPercentages(percentages, self.site)


class PollenPercentages(PollenSamples):
    def get_percentages(self, decimals=None):
        if decimals is None:
            return self
        else:
            return PollenPercentages(self.samples.round(decimals), self.site)


class StabilizedPollenSamples(PollenSamples):
    def __init__(self, samples, decimals, site=None):
        super().__init__(samples, site=site)
        self._decimals = decimals

    @property
    def decimals(self): return self._decimals

    def get_stabilized(self, default_threshold=0.0, decimals=2):
        # TODO: round if decimals are fewer than this is set up to use
        return self
