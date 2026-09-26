"""The satellite fronts adapter, offline: two fake satellite days, one known front in each.

A temperature step at 60.5 E and a chlorophyll edge at 61.5 E, on the real products' grid spacings
(1/20 and 1/24 degree), with latitude served north to south as ocean-colour files often are. The
share must land in the right platform cells, in both, and the kelvin must be read as kelvin.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest
import xarray as xr

from oceanverity.sources import copernicus_satellite
from oceanverity.sources.base import BoundingBox
from oceanverity.sources.copernicus_satellite import SST_DATASET, SatelliteFrontsSource

BOX = BoundingBox(south=0.0, north=1.0, west=60.0, east=62.0)
WHEN = datetime(2026, 7, 30, tzinfo=timezone.utc)
RNG = np.random.default_rng(3)


def fake_open(dataset_id, variable, bbox, timestep):
    if (dataset_id, variable) == SST_DATASET:
        lats = np.arange(0.025, 1.0, 0.05)
        lons = np.arange(60.025, 62.0, 0.05)
        values = np.where(lons < 60.5, 300.15, 301.65)[None, :].repeat(lats.size, 0)
        values = values + RNG.normal(0, 0.02, values.shape)
    else:
        lats = np.arange(1.0 - 1 / 48, 0.0, -1 / 24)  # north to south
        lons = np.arange(60 + 1 / 48, 62.0, 1 / 24)
        values = np.where(lons < 61.5, 0.1, 0.8)[None, :].repeat(lats.size, 0)
        values = values * np.exp(RNG.normal(0, 0.01, values.shape))
    return xr.Dataset(
        {variable: (("latitude", "longitude"), values)},
        coords={"latitude": lats, "longitude": lons},
    )


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(copernicus_satellite, "_open", fake_open)
    return SatelliteFrontsSource()


def test_each_front_lands_in_the_cell_it_is_in(offline):
    share, stats = offline.front_share(WHEN, BOX, np.array([0.5]), np.array([60.5, 61.5]))
    assert share.shape == (1, 2)
    # The 60.5 E step sits on the boundary between two cells' pixels; the 61.5 E edge likewise.
    assert stats["thermalPixels"] > 0 and stats["chlorophyllPixels"] > 0
    assert (share > 0).all()


def test_no_front_means_zero_not_mask(monkeypatch):
    def flat(dataset_id, variable, bbox, timestep):
        ds = fake_open(dataset_id, variable, bbox, timestep)
        ds[variable][:] = 300.0 if (dataset_id, variable) == SST_DATASET else 0.3
        return ds

    monkeypatch.setattr(copernicus_satellite, "_open", flat)
    share, stats = SatelliteFrontsSource().front_share(WHEN, BOX, np.array([0.5]), np.array([60.5, 61.5]))
    assert np.all(share == 0.0)
    assert stats["thermalPixels"] == 0 and stats["chlorophyllPixels"] == 0


def test_it_declares_one_drape_field_that_never_calls_itself_a_fishing_zone(offline):
    (spec,) = offline.fields()
    assert spec.key == "fronts" and spec.render == "column" and spec.isosurface is False
    text = f"{spec.label} {spec.description}".lower()
    assert "not a fishing zone" in text
    assert "fishing zone" not in text.replace("not a fishing zone", "")
