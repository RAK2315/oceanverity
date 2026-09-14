"""A named storm, held against the water it crossed.

Everything a storm case says is a distance or a before-and-after, and both produce believable
wrong numbers easily: a distance to the nearest *fix* rather than to the *track* flatters every
instrument between two fixes, and a before-and-after with nothing to compare it against cannot
tell a storm from a season. So both are held to hand-computable cases.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np
import pytest

from samudra.section import EARTH_RADIUS_KM
from samudra.storm import Fix, change_near_track, distance_to_track_km, read_best_track

KM_PER_DEGREE = EARTH_RADIUS_KM * math.pi / 180.0

CSV = """# IMD RSMC New Delhi best track, extracted for the test
time_utc,latitude,longitude,grade,wind_kt
2025-10-25T00:00:00Z,10.8,89.0,D,20
2025-10-25T03:00:00Z,10.8,88.8,D,25
2025-10-28T18:00:00Z,16.3,81.7,SCS,50
"""


def fix(lon, lat, hour=0):
    return Fix(time=datetime(2025, 10, 25, hour, tzinfo=timezone.utc), latitude=lat, longitude=lon, grade="D", wind_kt=20)


def test_the_best_track_is_read_in_order_with_its_grade_and_wind():
    fixes = read_best_track(CSV)
    assert len(fixes) == 3
    assert fixes[0].latitude == 10.8 and fixes[0].longitude == 89.0
    assert fixes[-1].grade == "SCS" and fixes[-1].wind_kt == 50
    assert fixes[0].time < fixes[1].time < fixes[2].time


def test_a_point_on_the_track_is_zero_away():
    track = [fix(80.0, 0.0), fix(82.0, 0.0)]
    assert distance_to_track_km(81.0, 0.0, track) == pytest.approx(0.0, abs=1e-6)


def test_distance_is_to_the_line_between_fixes_and_not_to_the_nearest_fix():
    """One degree north of the middle of an equatorial segment two degrees long. The nearest fix
    is 157 km away; the track is 111 km away, and 111 is the answer."""
    track = [fix(80.0, 0.0), fix(82.0, 0.0)]
    assert distance_to_track_km(81.0, 1.0, track) == pytest.approx(KM_PER_DEGREE, rel=1e-3)


def test_past_the_end_of_the_track_the_distance_is_to_the_end():
    """A storm that dissipated at 82 E did not pass 85 E, so a point beyond it is measured to
    where the track stopped, not to the track's line extended."""
    track = [fix(80.0, 0.0), fix(82.0, 0.0)]
    assert distance_to_track_km(85.0, 0.0, track) == pytest.approx(3 * KM_PER_DEGREE, rel=1e-3)


def test_the_nearest_segment_wins_on_a_bending_track():
    track = [fix(80.0, 0.0), fix(82.0, 0.0), fix(82.0, 3.0)]
    assert distance_to_track_km(82.5, 2.0, track) == pytest.approx(0.5 * KM_PER_DEGREE, rel=5e-3)


def test_the_change_near_the_track_is_set_beside_water_far_from_it():
    """A 3 x 3 box with the track down the middle column. Near cells deepen by 20 m, far cells
    by 2 m, and the result keeps the two apart rather than pooling them."""
    lats = np.array([0.0, 1.0, 2.0])
    lons = np.array([80.0, 83.0, 86.0])
    before = np.full((3, 3), 10.0)
    after = np.array([[12.0, 30.0, 12.0]] * 3)
    track = [fix(83.0, -1.0), fix(83.0, 3.0)]
    result = change_near_track(before, after, lats, lons, track, near_km=150.0, far_km=250.0)
    assert result.near.cells == 3
    assert result.near.median_before == 10.0 and result.near.median_after == 30.0
    assert result.near.share_increased == 1.0
    assert result.far.cells == 6
    assert result.far.median_after == 12.0


def test_cells_either_side_can_be_missing_and_are_left_out():
    lats = np.array([0.0])
    lons = np.array([83.0, 84.0])
    before = np.array([[10.0, np.nan]])
    after = np.array([[20.0, 20.0]])
    track = [fix(83.0, -1.0), fix(83.0, 1.0)]
    result = change_near_track(before, after, lats, lons, track, near_km=150.0, far_km=500.0)
    assert result.near.cells == 1
