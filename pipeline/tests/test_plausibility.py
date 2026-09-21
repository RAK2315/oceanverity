"""A provider's value that no sea has ever held is masked, counted, and never silently kept.

INCOIS's temperature analysis carries cells that are not water: 48.66 degC at 30 m in the Gulf
of Oman, and -3.36 degC, which is below the freezing point of seawater. The Volume never showed
them, because every range is percentile-clipped, but `Grid.column_at` reads them for the tooltip
and the section, and CF, OPeNDAP and WMS served them as published.

Masking a provider's numbers is rank 2 in `docs/BUGS.md` - data quietly discarded - so the mask
is allowed only on three conditions, and these tests hold all three: the bound is a physical
one with a stated source rather than a percentile, a masked cell becomes Mask (absence of
ocean, NaN) rather than a clamped value that would look like a measurement, and every masked
cell is counted so the manifest can say how many.
"""

from __future__ import annotations

import numpy as np
import pytest

from oceanverity.grid import Grid
from oceanverity.plausibility import TEMPERATURE_BOUNDS, mask_implausible

LEVELS = np.array([5.0, 30.0])
LATITUDES = np.array([24.5, 25.5])
LONGITUDES = np.array([56.5, 57.5])


def grid_with(values) -> Grid:
    return Grid(levels=LEVELS, latitudes=LATITUDES, longitudes=LONGITUDES,
                values=np.asarray(values, dtype=float))


def test_a_value_past_either_bound_becomes_mask_and_is_counted():
    values = np.full((2, 2, 2), 27.0)
    values[1, 0, 0] = 48.66
    values[0, 1, 1] = -3.36
    masked, count = mask_implausible(grid_with(values), *TEMPERATURE_BOUNDS)
    assert count == 2
    assert np.isnan(masked.values[1, 0, 0]) and np.isnan(masked.values[0, 1, 1])


def test_real_water_is_untouched_including_a_record_hot_gulf_surface():
    """37.6 degC is the verified in-situ record for the Persian Gulf, so it must survive."""
    values = np.full((2, 2, 2), 27.0)
    values[0, 0, 0] = 37.6
    values[1, 1, 1] = -1.9
    masked, count = mask_implausible(grid_with(values), *TEMPERATURE_BOUNDS)
    assert count == 0
    np.testing.assert_array_equal(masked.values, values)


def test_existing_mask_is_neither_counted_nor_changed():
    """Land was already absent. Counting it would inflate the figure the manifest reports."""
    values = np.full((2, 2, 2), 27.0)
    values[:, 0, 0] = np.nan
    masked, count = mask_implausible(grid_with(values), *TEMPERATURE_BOUNDS)
    assert count == 0
    assert np.isnan(masked.values[:, 0, 0]).all()


def test_the_input_grid_is_not_modified():
    """The caller may still hold the original; a mask applied in place would hide the evidence."""
    values = np.full((2, 2, 2), 27.0)
    values[0, 0, 0] = 45.0
    original = grid_with(values)
    mask_implausible(original, *TEMPERATURE_BOUNDS)
    assert original.values[0, 0, 0] == 45.0


def test_the_bounds_are_physical_and_not_fitted_to_this_bake():
    """Below seawater's freezing point, and above the verified record for the hottest sea."""
    low, high = TEMPERATURE_BOUNDS
    assert low < -1.9
    assert high > 37.6


def test_bounds_the_wrong_way_round_are_refused():
    with pytest.raises(ValueError):
        mask_implausible(grid_with(np.zeros((2, 2, 2))), 38.0, -2.5)
