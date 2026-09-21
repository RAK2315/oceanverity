"""The oxygen floor: how deep the water still holds enough oxygen for fish.

Held to hand-computable columns, because a wrong threshold or a wrong crossing produces a sheet
that is smooth, finite and entirely believable - the failure `hazard.py` is tested against too.
"""

from __future__ import annotations

import numpy as np
import pytest

from oceanverity.grid import Grid
from oceanverity.habitat import OXYGEN_FLOOR_MMOL, oxygen_floor

LEVELS = np.array([5.0, 10.0, 20.0, 30.0, 50.0, 75.0, 100.0, 125.0, 150.0, 200.0])


def columns(*profiles) -> Grid:
    values = np.array(profiles, dtype=float).reshape(1, len(profiles), LEVELS.size).transpose(2, 0, 1)
    return Grid(levels=LEVELS, latitudes=np.array([10.5]), longitudes=np.arange(len(profiles)) + 60.5, values=values)


def test_the_threshold_is_two_milligrams_a_litre():
    """2 mg/L of O2 at 32 g/mol is 62.5 mmol/m3, the usual line for hypoxic water."""
    assert OXYGEN_FLOOR_MMOL == pytest.approx(2.0 / 32.0 * 1000.0)


def test_the_floor_is_interpolated_between_the_two_levels_it_falls_between():
    # 100 at 75 m, 50 at 100 m: 62.5 is three quarters of the way down, at 93.75 m.
    grid = columns([200, 200, 200, 200, 190, 100, 50, 40, 30, 20])
    assert oxygen_floor(grid)[0, 0] == pytest.approx(93.75)


def test_a_column_that_never_runs_low_has_no_floor():
    """NaN, not 200 m: the water held enough oxygen as deep as this grid reaches."""
    grid = columns([210, 205, 200, 190, 180, 170, 160, 150, 140, 130])
    assert np.isnan(oxygen_floor(grid)[0, 0])


def test_the_first_crossing_from_the_surface_is_the_floor():
    """A column that recovers below a low layer still has its floor at the top of the low layer,
    because a fish swimming down meets that first."""
    grid = columns([200, 200, 200, 200, 200, 100, 50, 40, 90, 150])
    assert oxygen_floor(grid)[0, 0] == pytest.approx(93.75)


def test_land_has_no_floor():
    grid = columns([np.nan] * LEVELS.size)
    assert np.isnan(oxygen_floor(grid)[0, 0])


def test_each_column_is_answered_on_its_own():
    grid = columns([200, 200, 200, 200, 190, 100, 50, 40, 30, 20], [210, 205, 200, 190, 180, 170, 160, 150, 140, 130])
    out = oxygen_floor(grid)
    assert out.shape == (1, 2)
    assert out[0, 0] == pytest.approx(93.75) and np.isnan(out[0, 1])
