# Copyright 2020 Peter Liljenberg <peter.liljenberg@gmail.com>
# Open source under the MIT license (see LICENSE)

# pylint: disable=import-error

from __future__ import annotations

import numpy as np
import pandas as pd
import gspread
from collections import Counter

class PollenSamples:
    sample_type = None

    def __init__(self, samples: pd.DataFrame, site: str=None):
        self._samples = samples
        self._site = site

    @classmethod
    def read_csv(cls, filepath_or_buffer, site=None, index_col=0, **kwargs) -> PollenSamples:
        return PollenSamples._read_csv(cls, filepath_or_buffer, site=site, index_col=index_col, **kwargs)
    
    @staticmethod
    def _read_csv(constructor, filepath_or_buffer, site, index_col, **kwargs):
        df = pd.read_csv(filepath_or_buffer, index_col=index_col, header=0, **kwargs)
        return constructor(df, site=site)

    @classmethod
    def read_google_sheet(cls, worksheet: gspread.worksheet.Worksheet, index_col=0) -> PollenSamples:
        return PollenSamples._read_google_sheet(cls, cls.sample_type, worksheet, index_col)

    @staticmethod
    def _read_google_sheet(constructor, sample_type, worksheet, index_col):
        rows = worksheet.get_all_values(value_render_option='UNFORMATTED_VALUE')
        columns = [c.strip() for c in rows[0]]

        duplicates = [col for col, cnt in Counter(columns).items() if cnt > 1]
        if duplicates:
            raise ValueError(f'Duplicate columns in {worksheet.title}: {duplicates}')

        if isinstance(index_col, int):
            index_col = [index_col]

        def parse_row(row):
            return [sample_type(v or 0) if colnum not in index_col else v
                    for colnum, v in enumerate(row)]

        data = [parse_row(row) for row in rows[1:]]
        index = [columns[i] for i in index_col]

        return constructor(pd.DataFrame.from_records(data, columns=columns, index=index), site=worksheet.title)

    @property
    def samples(self) -> pd.DataFrame: return self._samples

    @property
    def taxas(self) -> pd.Index[str]: return self._samples.columns
        
    @property
    def site(self) -> str: return self._site

    def apply(self, sample_func) -> PollenSamples:
        raise NotImplementedError()

    def get_percentages(self, decimals: int=None) -> PollenPercentages: 
        raise NotImplementedError()

    def get_stabilized(self, default_threshold: float=0.0, decimals: int=2) -> StabilizedPollenSamples:
        percentages = self.get_percentages()

        # TODO: support per-taxa thresholds
        stabilized = (percentages.samples
                        .sub(default_threshold)
                        .clip(lower=0)
                        .apply(np.sqrt)
                        .round(decimals))

        return StabilizedPollenSamples(stabilized, site=self.site, decimals=decimals)

    def to_csv(self, path_or_buf, decimals=2, **kwargs):
        self.samples.to_csv(path_or_buf, float_format='%.{}f'.format(decimals), **kwargs)


class PollenCounts(PollenSamples):
    sample_type = int

    def apply(self, sample_func) -> PollenCounts:
        return PollenCounts(sample_func(self._samples), self._site)

    def get_percentages(self, decimals=None) -> PollenPercentages: 
        sums = self.samples.sum(axis=1)
        percentages = self.samples.apply(lambda column: column * 100 / sums).fillna(0.0)

        if decimals is not None:
            percentages = percentages.round(decimals)

        return PollenPercentages(percentages, self.site)


class PollenPercentages(PollenSamples):
    sample_type = float

    def apply(self, sample_func) -> PollenPercentages:
        return PollenPercentages(sample_func(self._samples), self._site)

    def get_percentages(self, decimals=None) -> PollenPercentages:
        if decimals is None:
            return self
        else:
            return PollenPercentages(self.samples.round(decimals), self.site)


class StabilizedPollenSamples(PollenSamples):
    sample_type = float

    def __init__(self, samples: pd.DataFrame, decimals:int, site=None):
        super().__init__(samples, site=site)
        self._decimals = decimals

    @property
    def decimals(self) -> int: return self._decimals

    def apply(self, sample_func) -> StabilizedPollenSamples:
        return StabilizedPollenSamples(sample_func(self._samples).round(self._decimals), self._decimals, self._site)

    def get_stabilized(self, default_threshold=0.0, decimals=2) -> StabilizedPollenSamples:
        # TODO: round if decimals are fewer than this is set up to use
        return self

    @classmethod
    def read_csv(cls, filepath_or_buffer, decimals, site=None, index_col=0, **kwargs):
        return PollenSamples._read_csv(lambda samples, site=None: cls(samples, decimals, site=site), filepath_or_buffer, site=site, index_col=index_col, **kwargs)

    @classmethod
    def read_google_sheet(cls, worksheet: gspread.worksheet.Worksheet, decimals: int, index_col=0):
        return PollenSamples._read_google_sheet(lambda samples, site=None: cls(samples, decimals, site=site), cls.sample_type, worksheet, index_col)

    def to_csv(self, path_or_buf, decimals=None, **kwargs):
        if decimals is None:
            decimals = self.decimals

        super().to_csv(path_or_buf, decimals=decimals, **kwargs)

    @staticmethod
    def _parse_sample_string(s):
        return float(s) if s else 0.0
