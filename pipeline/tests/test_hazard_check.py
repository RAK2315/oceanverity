"""Our hazard surfaces held against INCOIS's published ones.

The arithmetic is small and that is exactly why it is tested: an agreement figure that silently
counts land as agreement, or drops the cells one side could not compute, would be a flattering
number that nothing downstream could catch.
"""

from __future__ import annotations

import numpy as np
import pytest

from oceanverity.hazard_check import EXACT_METRES, agreement


def test_identical_surfaces_agree_completely():
    surface = np.array([[10.0, 20.0], [30.0, 40.0]])
    result = agreement(surface, surface.copy())
    assert result.cells == 4
    assert result.exact_share == 1.0
    assert result.median_abs_metres == 0.0
    assert result.median_signed_metres == 0.0


def test_the_sign_says_which_side_is_deeper():
    """Ours minus theirs, the same way round as a Residual: negative means ours is shallower."""
    ours = np.array([[10.0, 20.0, 30.0]])
    theirs = np.array([[15.0, 25.0, 35.0]])
    result = agreement(ours, theirs)
    assert result.median_signed_metres == pytest.approx(-5.0)
    assert result.median_abs_metres == pytest.approx(5.0)
    assert result.exact_share == 0.0


def test_only_cells_both_sides_computed_are_compared():
    """Land, and a column one side could not resolve, are not agreement and not disagreement.
    They are left out and the count says how many were left in."""
    ours = np.array([[10.0, np.nan, 30.0, 40.0]])
    theirs = np.array([[10.0, 20.0, np.nan, 41.0]])
    result = agreement(ours, theirs)
    assert result.cells == 2
    assert result.exact_share == pytest.approx(0.5)


def test_exact_allows_only_float_storage_noise():
    ours = np.array([[50.0, 50.0]])
    theirs = np.array([[50.0 + EXACT_METRES / 2, 50.0 + EXACT_METRES * 4]])
    assert agreement(ours, theirs).exact_share == pytest.approx(0.5)
    assert EXACT_METRES <= 0.05, "exact means the same number, not a close one"


def test_many_dates_pool_cell_by_cell_rather_than_averaging_averages():
    first = (np.array([[10.0]]), np.array([[10.0]]))
    second = (np.array([[10.0, 20.0, 30.0]]), np.array([[11.0, 22.0, 33.0]]))
    result = agreement(*zip(first, second))
    assert result.cells == 4
    assert result.exact_share == pytest.approx(0.25)


def test_a_high_exact_share_does_not_hide_how_far_the_rest_are():
    """97% exact reads as perfect. The size of the gap in the other 3% is reported beside it."""
    ours = np.array([[10.0, 10.0, 10.0, 10.0]])
    theirs = np.array([[10.0, 10.0, 30.0, 50.0]])
    result = agreement(ours, theirs)
    assert result.median_abs_metres == pytest.approx(10.0)
    assert result.median_abs_where_different == pytest.approx(30.0)
    assert np.isnan(agreement(ours, ours.copy()).median_abs_where_different)


def test_nothing_to_compare_is_refused_rather_than_reported_as_zero():
    with pytest.raises(ValueError):
        agreement(np.array([[np.nan]]), np.array([[1.0]]))
