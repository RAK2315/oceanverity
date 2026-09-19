"""The World Ocean Atlas adapter, and the three routes it has to the same numbers.

NOAA's OPeNDAP server for WOA23 timed out on 2026-09-14 and answered 503 on 2026-09-15, while the
plain HTTPS file server beside it answered 200. A bake that read only OPeNDAP lost Temperature vs
Normal on both days. So the adapter reads, in order: a regional subset already saved under
`data/woa/`, then OPeNDAP, then the whole file over HTTPS. Whatever route answers, the subset it
produced is saved, so the next bake needs no network for it at all.

No test here touches the network: the two remote routes are injected.
"""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from samudra.sources.base import BoundingBox
from samudra.sources.woa import WoaClimatologySource

BOX = BoundingBox(south=-9.5, north=25.5, west=45.5, east=100.5)
FILL = 9.96921e36


def global_month(value: float = 20.0) -> xr.Dataset:
    """A tiny stand-in for one WOA file: the real axis convention, a fill value on one node."""
    lat = np.arange(-89.5, 90.0, 1.0)
    lon = np.arange(-179.5, 180.0, 1.0)
    depth = np.array([0.0, 5.0, 10.0])
    data = np.full((1, depth.size, lat.size, lon.size), value, dtype="float32")
    data[0, :, 100, 250] = FILL  # 10.5 N, 70.5 E is "land"
    t_an = xr.DataArray(data, dims=("time", "depth", "lat", "lon"))
    t_an.attrs["_FillValue"] = FILL
    return xr.Dataset({"t_an": t_an}, coords={"lat": lat, "lon": lon, "depth": depth})


def failing(*_):
    raise OSError("503 Service Unavailable")


def test_opendap_is_tried_first_and_its_subset_is_saved(tmp_path):
    source = WoaClimatologySource(cache_dir=tmp_path, open_opendap=lambda url: global_month(), open_https=failing)
    grid = source.fetch_grid("temperature", 7, BOX)
    assert grid.latitudes[0] == pytest.approx(-9.5) and grid.latitudes[-1] == pytest.approx(25.5)
    assert grid.longitudes[0] == pytest.approx(45.5) and grid.longitudes[-1] == pytest.approx(100.5)
    assert list(tmp_path.glob("*.npz")), "the subset was not saved"


def test_https_answers_when_opendap_is_down(tmp_path):
    source = WoaClimatologySource(cache_dir=tmp_path, open_opendap=failing, open_https=lambda url: global_month(21.0))
    grid = source.fetch_grid("temperature", 7, BOX)
    assert np.nanmax(grid.values) == pytest.approx(21.0)
    assert source.last_route == "https"


def test_a_saved_subset_needs_no_network(tmp_path):
    WoaClimatologySource(cache_dir=tmp_path, open_opendap=lambda url: global_month(22.0), open_https=failing).fetch_grid("temperature", 7, BOX)
    offline = WoaClimatologySource(cache_dir=tmp_path, open_opendap=failing, open_https=failing)
    grid = offline.fetch_grid("temperature", 7, BOX)
    assert np.nanmax(grid.values) == pytest.approx(22.0)
    assert offline.last_route == "cache"


def test_a_saved_subset_is_cut_down_to_a_smaller_box(tmp_path):
    WoaClimatologySource(cache_dir=tmp_path, open_opendap=lambda url: global_month(), open_https=failing).fetch_grid("temperature", 7, BOX)
    small = BoundingBox(south=0.5, north=10.5, west=60.5, east=70.5)
    grid = WoaClimatologySource(cache_dir=tmp_path, open_opendap=failing, open_https=failing).fetch_grid("temperature", 7, small)
    assert grid.values.shape[1:] == (11, 11)


def test_a_saved_subset_that_does_not_cover_the_box_is_not_used(tmp_path):
    small = BoundingBox(south=0.5, north=10.5, west=60.5, east=70.5)
    WoaClimatologySource(cache_dir=tmp_path, open_opendap=lambda url: global_month(), open_https=failing).fetch_grid("temperature", 7, small)
    with pytest.raises(OSError):
        WoaClimatologySource(cache_dir=tmp_path, open_opendap=failing, open_https=failing).fetch_grid("temperature", 7, BOX)


def test_the_fill_value_is_mask_whichever_route_answered(tmp_path):
    for route in ("opendap", "https"):
        folder = tmp_path / route
        opener = lambda url: global_month()  # noqa: E731
        source = WoaClimatologySource(
            cache_dir=folder,
            open_opendap=opener if route == "opendap" else failing,
            open_https=opener if route == "https" else failing,
        )
        grid = source.fetch_grid("temperature", 7, BOX)
        row = int(np.argmin(np.abs(grid.latitudes - 10.5)))
        column = int(np.argmin(np.abs(grid.longitudes - 70.5)))
        assert np.isnan(grid.values[:, row, column]).all()
        assert np.nanmax(np.abs(grid.values)) < 1e30


def test_both_routes_down_and_nothing_saved_raises(tmp_path):
    with pytest.raises(OSError):
        WoaClimatologySource(cache_dir=tmp_path, open_opendap=failing, open_https=failing).fetch_grid("temperature", 7, BOX)


def test_the_https_address_is_the_file_server_beside_opendap():
    source = WoaClimatologySource()
    assert source.https_url_for("temperature", 7) == (
        "https://www.ncei.noaa.gov/data/oceans/woa/WOA23/DATA/temperature/netcdf/decav91C0/1.00/"
        "woa23_decav91C0_t07_01.nc"
    )
