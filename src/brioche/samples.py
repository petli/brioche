# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

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

    def get_percentages(self):
        raise NotImplementedError()
       

class PollenCounts(PollenSamples):
    def get_percentages(self): 
        sums = self.samples.sum(axis=1)
        percentages = self.samples.apply(lambda column: column * 100 / sums)
        return PollenPercentages(percentages, self.site)


class PollenPercentages(PollenSamples):
    def get_percentages(self): 
        return self
