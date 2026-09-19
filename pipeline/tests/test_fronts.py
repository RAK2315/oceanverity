"""Fronts: the edges between two bodies of surface water, which is where fish gather.

INCOIS build their Potential Fishing Zone advisories from exactly these: thermal fronts in sea
surface temperature and chlorophyll fronts in ocean colour. They name the methods - Cayula and
Cornillon (1992) for temperature, Canny for chlorophyll. This module follows those two methods on
Copernicus satellite fields for every Timestep, so the platform can show the ingredient **without
calling the result a fishing zone**, which it is not.

Every test here is a synthetic field whose answer is known by construction: a sharp step has a
front on it, a uniform field and a smooth gentle slope have none, and noise alone is not a front.
"""

from __future__ import annotations

import numpy as np
import pytest

from samudra.fronts import chlorophyll_fronts, front_share, thermal_fronts

RNG = np.random.default_rng(7)


def step_field(low: float, high: float, shape=(64, 64), column=32, noise=0.02):
    field = np.full(shape, low, dtype=float)
    field[:, column:] = high
    return field + RNG.normal(0.0, noise, shape)


# ---------------------------------------------------------------- thermal: Cayula-Cornillon

def test_a_sharp_step_in_temperature_is_a_front_along_the_step():
    sst = step_field(27.0, 28.5)
    fronts = thermal_fronts(sst)
    columns = np.where(fronts.any(axis=0))[0]
    assert fronts.sum() > 0
    assert set(columns) <= {31, 32}, columns
    # Found along most of the step, not in one spot.
    assert fronts[:, 31:33].any(axis=1).mean() > 0.8


def test_a_uniform_sea_has_no_thermal_front():
    assert not thermal_fronts(np.full((64, 64), 28.0) + RNG.normal(0, 0.02, (64, 64))).any()


@pytest.mark.parametrize("span", [2.0, 6.0, 12.0])
def test_a_steady_slope_is_not_a_front_however_steep(span):
    """A slope has one population of temperatures, not two, so it is a gradient rather than an
    edge between two bodies of water. At six and twelve degrees the two halves of a window differ
    by far more than the minimum contrast, so only the bimodality test can refuse it."""
    slope = np.tile(np.linspace(27.0, 27.0 + span, 64), (64, 1)) + RNG.normal(0, 0.02, (64, 64))
    assert not thermal_fronts(slope).any()


def test_a_step_smaller_than_the_minimum_contrast_is_not_a_front():
    """0.2 degC between the two bodies is below what the method accepts as two populations."""
    assert not thermal_fronts(step_field(28.0, 28.2)).any()


def test_land_is_never_a_front_and_does_not_make_one():
    sst = np.full((64, 64), 28.0) + RNG.normal(0, 0.02, (64, 64))
    sst[:, 40:] = np.nan
    assert not thermal_fronts(sst).any()


# ---------------------------------------------------------------- chlorophyll: Canny

def test_a_sharp_edge_in_chlorophyll_is_a_front_along_the_edge():
    chl = np.exp(step_field(np.log(0.1), np.log(0.8), noise=0.01))
    fronts = chlorophyll_fronts(chl)
    columns = np.where(fronts.any(axis=0))[0]
    assert fronts.sum() > 0
    assert set(columns) <= {30, 31, 32, 33}, columns
    assert fronts[:, 30:34].any(axis=1).mean() > 0.8


def test_the_edge_is_thin_not_a_smear():
    """Canny keeps only the ridge of the gradient, so an edge is about one pixel wide."""
    chl = np.exp(step_field(np.log(0.1), np.log(0.8), noise=0.01))
    fronts = chlorophyll_fronts(chl)
    assert fronts[10:54].sum(axis=1).max() <= 2


def test_uniform_chlorophyll_has_no_front():
    chl = np.exp(np.log(0.3) + RNG.normal(0, 0.01, (64, 64)))
    assert not chlorophyll_fronts(chl).any()


def test_chlorophyll_is_read_on_a_log_scale():
    """0.05 to 0.1 mg/m3 is the same doubling as 1 to 2. Both are fronts, or neither is."""
    open_ocean = chlorophyll_fronts(np.exp(step_field(np.log(0.05), np.log(0.1), noise=0.005)))
    coastal = chlorophyll_fronts(np.exp(step_field(np.log(1.0), np.log(2.0), noise=0.005)))
    assert open_ocean.sum() == pytest.approx(coastal.sum(), abs=4)


def test_a_chlorophyll_field_with_land_does_not_draw_the_coast_as_a_front():
    chl = np.exp(np.log(0.3) + RNG.normal(0, 0.01, (64, 64)))
    chl[:, 40:] = np.nan
    assert not chlorophyll_fronts(chl).any()


# ---------------------------------------------------------------- onto the platform's cells

def test_the_share_is_the_fraction_of_a_cells_ocean_pixels_on_a_front():
    fine_lats = np.arange(0.025, 2.0, 0.05)  # 40 rows, two 1-degree cells
    fine_lons = np.arange(60.025, 61.0, 0.05)  # 20 columns, one cell
    mask = np.zeros((40, 20), dtype=bool)
    mask[:20, :5] = True  # a quarter of the southern cell
    ocean = np.ones((40, 20), dtype=bool)
    ocean[20:, :10] = False  # half of the northern cell is land
    mask[20:, 10:12] = True  # 40 of its 200 ocean pixels
    share = front_share(mask, ocean, fine_lats, fine_lons, np.array([0.5, 1.5]), np.array([60.5]))
    assert share.shape == (2, 1)
    assert share[0, 0] == pytest.approx(25.0)
    assert share[1, 0] == pytest.approx(20.0)


def test_a_cell_with_no_ocean_pixels_is_mask_not_zero():
    fine_lats = np.arange(0.025, 1.0, 0.05)
    fine_lons = np.arange(60.025, 61.0, 0.05)
    share = front_share(
        np.zeros((20, 20), bool), np.zeros((20, 20), bool), fine_lats, fine_lons, np.array([0.5]), np.array([60.5])
    )
    assert np.isnan(share[0, 0])


def test_a_front_on_a_finer_grid_lands_in_the_coarser_pixel_that_contains_it():
    """Chlorophyll comes at 1/24 degree and temperature at 1/20. Every chlorophyll front pixel must
    reach the temperature pixel whose footprint holds it, or a thin edge could fall between the
    samples of a nearest-neighbour lookup and vanish."""
    from samudra.fronts import onto_grid

    fine_lats = np.arange(1 / 48, 1.0, 1 / 24)
    fine_lons = np.arange(60 + 1 / 48, 61.0, 1 / 24)
    mask = np.zeros((fine_lats.size, fine_lons.size), dtype=bool)
    mask[:, 7] = True  # a north-south line at 60.3125 E
    coarse_lats = np.arange(0.025, 1.0, 0.05)
    coarse_lons = np.arange(60.025, 61.0, 0.05)
    out = onto_grid(mask, fine_lats, fine_lons, coarse_lats, coarse_lons)
    assert out.shape == (20, 20)
    assert np.where(out.any(axis=0))[0].tolist() == [6]  # 60.30 to 60.35 E
    assert out[:, 6].all()


def test_a_fine_pixel_outside_the_coarse_grid_is_dropped():
    from samudra.fronts import onto_grid

    out = onto_grid(np.ones((1, 1), bool), np.array([5.0]), np.array([60.0]), np.array([0.025]), np.array([60.025]))
    assert not out.any()
