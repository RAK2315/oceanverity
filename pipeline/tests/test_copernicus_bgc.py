"""The biogeochemistry adapter: the seam's contract, and the nearest-node rule it shares.

The network half needs a Copernicus credential, so `_open` is replaced with an in-memory day shaped
like the real one: 0.25 degree nodes, a few depths, a land cell. What is tested is the adapter's
contract and how a 0.25 degree product lands on the platform's 1 degree nodes.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pytest
import xarray as xr

from samudra.sources import copernicus_bgc
from samudra.sources.base import BoundingBox
from samudra.sources.copernicus import land_on_axes
from samudra.sources.copernicus_bgc import CopernicusBgcSource

BOX = BoundingBox(south=0.0, north=2.0, west=60.0, east=62.0)
WHEN = datetime(2026, 7, 30, tzinfo=timezone.utc)


def quarter_degree_day(dataset_id, variable, bbox, timestep):
    """Each value encodes where it is: 1000 * depth index + 10 * lat + lon offset."""
    depth = np.array([0.5, 5.1, 10.5, 100.0])
    lat = np.arange(-1.0, 3.01, 0.25)
    lon = np.arange(59.0, 63.01, 0.25)
    d, y, x = np.meshgrid(np.arange(depth.size), lat, lon - 59.0, indexing="ij")
    values = 1000.0 * d + 10.0 * y + x
    values[:, 8, 8] = np.nan  # 1.0 N, 61.0 E is land
    return xr.Dataset(
        {variable: (("depth", "latitude", "longitude"), values)},
        coords={"depth": depth, "latitude": lat, "longitude": lon},
    )


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(copernicus_bgc, "_open", quarter_degree_day)
    return CopernicusBgcSource()


def test_every_field_the_adapter_declares_can_be_fetched(offline):
    for spec in offline.fields():
        grid = offline.fetch_grid(spec.key, WHEN, BOX)
        assert grid.values.ndim == 3, spec.key


def test_it_declares_chlorophyll_and_oxygen_in_the_biology_group(offline):
    keys = {spec.key: spec for spec in offline.fields()}
    assert set(keys) == {"chlorophyll", "oxygen"}
    assert keys["chlorophyll"].units == "mg/m³"
    assert keys["oxygen"].units == "mmol/m³"
    assert {spec.group for spec in keys.values()} == {"biology"}


def test_a_field_lands_on_the_model_nodes_by_nearest_source_node(offline):
    """1.5 N, 60.5 E at 5 m takes the source value published exactly there, not a box mean."""
    grid = offline.fetch_on_axes(
        "oxygen", WHEN, BOX, levels=[5.0, 100.0], latitudes=[0.5, 1.5], longitudes=[60.5, 61.5]
    )
    assert grid.values.shape == (2, 2, 2)
    assert grid.values[0, 1, 0] == pytest.approx(1000.0 * 1 + 10.0 * 1.5 + 1.5)
    assert grid.values[1, 0, 1] == pytest.approx(1000.0 * 3 + 10.0 * 0.5 + 2.5)


def test_land_in_the_source_stays_land_on_the_model_node(offline):
    grid = offline.fetch_on_axes("chlorophyll", WHEN, BOX, levels=[5.0], latitudes=[1.0], longitudes=[61.0])
    assert np.isnan(grid.values).all()


def test_an_unknown_key_is_refused_by_name(offline):
    with pytest.raises(KeyError, match="chlorophyll"):
        offline.fetch_grid("temperature", WHEN, BOX)


def test_the_shared_landing_rule_keeps_the_axes_it_was_given():
    day = quarter_degree_day("x", "chl", BOX, WHEN)
    grid = land_on_axes(day, "chl", [10.0], [0.5, 1.5], [60.5])
    assert list(grid.levels) == [10.0]
    assert list(grid.latitudes) == [0.5, 1.5]
    assert list(grid.longitudes) == [60.5]
