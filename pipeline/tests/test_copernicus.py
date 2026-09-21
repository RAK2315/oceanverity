"""The Copernicus adapter honours the seam's own contract: ask it for a Field it declares.

`fields()` declares exactly one Field, `current_speed`, and `fetch_grid` used to know only
`current_u` and `current_v` - so the one key the adapter advertised was the one key it raised
`KeyError` on. Nothing called it, because the bake fetches both components on the model's axes
and the API reads `.npz` from disk, which is exactly how a broken contract survives: the
docstring promised the registry could hand it straight to the CF and OPeNDAP writers, and it
could not.

The network half needs a Copernicus credential, so `_open` is replaced with an in-memory dataset
shaped like the real one. What is tested is the adapter's arithmetic and its contract, not the
download.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest
import xarray as xr

from oceanverity.sources import copernicus
from oceanverity.sources.base import BoundingBox
from oceanverity.sources.copernicus import CopernicusCurrentsSource

BOX = BoundingBox(south=0.0, north=2.0, west=60.0, east=62.0)
WHEN = datetime(2026, 7, 30, tzinfo=timezone.utc)


def fake_day(bbox, timestep):
    """3 m/s east and 4 m/s north everywhere, so the speed is exactly 5, with one land cell."""
    depth = np.array([0.5, 10.0])
    lat = np.array([0.0, 1.0, 2.0])
    lon = np.array([60.0, 61.0, 62.0])
    uo = np.full((2, 3, 3), 3.0)
    vo = np.full((2, 3, 3), 4.0)
    uo[:, 0, 0] = np.nan
    vo[:, 0, 0] = np.nan
    return xr.Dataset(
        {
            "uo": (("depth", "latitude", "longitude"), uo),
            "vo": (("depth", "latitude", "longitude"), vo),
        },
        coords={"depth": depth, "latitude": lat, "longitude": lon},
    )


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(copernicus, "_open", fake_day)
    return CopernicusCurrentsSource()


def test_every_field_the_adapter_declares_can_be_fetched(offline):
    """The contract, stated as the Protocol states it."""
    for spec in offline.fields():
        grid = offline.fetch_grid(spec.key, WHEN, BOX)
        assert grid.values.shape == (2, 3, 3), spec.key


def test_current_speed_is_the_magnitude_of_the_two_components(offline):
    grid = offline.fetch_grid("current_speed", WHEN, BOX)
    assert np.nanmax(grid.values) == pytest.approx(5.0)
    assert np.nanmin(grid.values) == pytest.approx(5.0)


def test_land_stays_land_in_the_speed(offline):
    """NaN in, NaN out. A land cell with a speed of zero would read as still water."""
    grid = offline.fetch_grid("current_speed", WHEN, BOX)
    assert np.isnan(grid.values[:, 0, 0]).all()


def test_the_components_are_still_served(offline):
    assert np.nanmax(offline.fetch_grid("current_u", WHEN, BOX).values) == pytest.approx(3.0)
    assert np.nanmax(offline.fetch_grid("current_v", WHEN, BOX).values) == pytest.approx(4.0)


def test_an_unknown_key_is_refused_by_name(offline):
    """A bare KeyError('temperature') says nothing about what this adapter can serve."""
    with pytest.raises(KeyError, match="current_speed"):
        offline.fetch_grid("temperature", WHEN, BOX)
