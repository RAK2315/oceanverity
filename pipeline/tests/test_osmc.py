"""Moorings, from the real-time GTS feed.

PS 26067 asks that the design extend to CTDs, moorings, HF-radar and ADCP. The seam was real and
tested and nothing was plugged into it, which is a weaker claim than it sounds - so this wires
up the one class of instrument that is both reachable and *Indian*.

NOAA's OSMC feed flattens the whole Global Telecommunication System into one ERDDAP table, CC0,
no login. Measured over the demo region for a single ten-day window, 20-30 Jul 2026, it returns
100,405 rows of which 94,653 carry subsurface temperature, from 169 profiling floats, 13 generic
moored buoys, 2 tropical moored buoys, 122 ships and 14 drifters. Five of those moorings report a
real vertical profile: 23459, 23451 and 23452 are India's OMNI network, and 2300009 and 2300019
are RAMA, NOAA's array, run with MoES among its partners.

It is a genuinely different format from Argo's, which is the point: depth in metres rather than
pressure, one row per level per report, the surface value in a different column from every other
level, no per-value QC flags at all, and a platform type that decides how the thing is drawn.
Absorbing all of that happens here and stops here; nothing downstream of `Profile` changes.
"""

from __future__ import annotations

import numpy as np
import pytest

from oceanverity.sources.osmc import (
    MIN_PROFILE_LEVELS,
    OsmcSource,
    parse_osmc,
    reject_spikes,
    thin_to_one_per_day,
)

# Two reports from India's OMNI buoy 23459 in the Bay of Bengal, three hours apart, trimmed to
# six levels. Note the shape of the surface row: `ztmp` and `zsal` are empty at 0 m and the
# reading lives in `sst`/`sss` instead.
OMNI = """platform_code,platform_type,country,time,latitude,longitude,observation_depth,ztmp,zsal,sst,sss
,,,UTC,degrees_north,degrees_east,,Deg C,,Deg C,1
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T00:00:00Z,13.984,87.02,0.0,NaN,NaN,29.1,33.2
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T00:00:00Z,13.984,87.02,10.0,29.09,33.76,NaN,NaN
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T00:00:00Z,13.984,87.02,20.0,29.09,33.72,NaN,NaN
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T00:00:00Z,13.984,87.02,75.0,26.32,34.39,NaN,NaN
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T00:00:00Z,13.984,87.02,200.0,13.6,35.0,NaN,NaN
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T00:00:00Z,13.984,87.02,500.0,9.97,35.1,NaN,NaN
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T03:00:00Z,13.986,87.025,0.0,NaN,NaN,29.1,33.2
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T03:00:00Z,13.986,87.025,10.0,29.07,33.75,NaN,NaN
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T03:00:00Z,13.986,87.025,20.0,29.07,33.55,NaN,NaN
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T03:00:00Z,13.986,87.025,75.0,26.09,34.41,NaN,NaN
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T03:00:00Z,13.986,87.025,200.0,13.91,34.99,NaN,NaN
23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T03:00:00Z,13.986,87.025,500.0,10.14,35.1,NaN,NaN
"""

# A coastal buoy that only reports at the surface. Real, and common: about ten of these sit off
# Chennai, Visakhapatnam, Lakshadweep and the Andamans.
SURFACE_ONLY = """platform_code,platform_type,country,time,latitude,longitude,observation_depth,ztmp,zsal,sst,sss
,,,UTC,degrees_north,degrees_east,,Deg C,,Deg C,1
23099,MOORED BUOYS (GENERIC),INDIA,2026-07-25T00:00:00Z,13.09,80.31,0.0,NaN,NaN,29.9,32.0
23099,MOORED BUOYS (GENERIC),INDIA,2026-07-25T03:00:00Z,13.09,80.31,0.0,NaN,NaN,29.8,32.0
23099,MOORED BUOYS (GENERIC),INDIA,2026-07-25T06:00:00Z,13.09,80.31,0.0,NaN,NaN,30.0,32.1
"""


def test_one_profile_per_report():
    profiles = parse_osmc(OMNI)
    assert len(profiles) == 2
    assert {p.platform_id for p in profiles} == {"23459"}
    assert [len(p) for p in profiles] == [6, 6]


def test_the_surface_reading_comes_from_the_column_it_actually_lives_in():
    """`ztmp` is empty at 0 m and the value is in `sst`. Dropping the surface would throw away
    the level a fisheries or cyclone reader looks at first."""
    first = parse_osmc(OMNI)[0]
    assert first.depths[0] == pytest.approx(0.0)
    assert first.values["temperature"][0] == pytest.approx(29.1)
    assert first.values["salinity"][0] == pytest.approx(33.2)


def test_depth_is_taken_as_metres_and_not_run_through_the_pressure_conversion():
    """Argo reports pressure; this feed reports depth. Converting again would move the deepest
    level of an Indian mooring by about 12 m, which is the axis the whole comparison sits on."""
    deepest = parse_osmc(OMNI)[0].depths[-1]
    assert deepest == pytest.approx(500.0)


def test_a_mooring_is_carried_as_anchored_and_named_by_its_operator():
    profile = parse_osmc(OMNI)[0]
    assert profile.kind == "mooring"
    assert profile.country == "INDIA"


def test_a_surface_only_buoy_is_not_a_profile():
    """One point is a measurement, not a cast. It cannot be drawn against a water column, and
    the panel would have nothing to put on its depth axis."""
    assert parse_osmc(SURFACE_ONLY) == []


def test_the_minimum_is_stated_rather_than_hidden():
    assert MIN_PROFILE_LEVELS >= 4


def test_implausible_values_are_refused_per_channel():
    """A mooring's thermistor string fails the same way a float's does, and the feed carries no
    quality flags at all - so the regional plausible range is the only layer there is."""
    broken = OMNI.replace(",13.6,35.0,", ",13.6,2.0,")
    profile = parse_osmc(broken)[0]
    assert np.isfinite(profile.values["temperature"]).all()
    assert not np.isfinite(profile.values["salinity"][4])


def test_a_zero_reading_inside_warm_water_is_refused_as_a_spike():
    """The case that made this test exist. Buoy 23094, Bay of Bengal, September 2025, reported
    29.55 degC at 15 m, **0.0 degC at 20 m** and 29.58 degC at 30 m. Zero is inside the regional
    range, so the range check let it through, and it pushed the buoys' published typical gap from
    0.88 to 1.01 degC on its own. Argo's spike test is what catches it."""
    depths = np.array([0.0, 15.0, 20.0, 30.0, 75.0])
    temperature = np.array([32.3, 29.55, 0.0, 29.58, 28.95])
    cleaned = reject_spikes(depths, temperature, "temperature")
    assert not np.isfinite(cleaned[2])
    assert np.isfinite(np.delete(cleaned, 2)).all()


def test_a_sharp_thermocline_is_a_step_and_not_a_spike():
    """The second term of the test value is what spares a real gradient: a reading halfway
    through a steep drop is not different from its neighbours in the way a spike is."""
    depths = np.array([10.0, 20.0, 40.0, 60.0])
    temperature = np.array([29.0, 28.9, 22.0, 18.0])
    assert np.isfinite(reject_spikes(depths, temperature, "temperature")).all()


def test_the_temperature_threshold_tightens_from_500_m():
    """Argo QC manual v3.9, test 9: 6.0 degC above 500 dbar, 2.0 degC at or below it. A test
    value of 2.5 degC fails deep and passes shallow."""
    values = np.array([11.0, 13.5, 8.0])
    shallow = reject_spikes(np.array([200.0, 400.0, 450.0]), values, "temperature")
    deep = reject_spikes(np.array([300.0, 500.0, 750.0]), values, "temperature")
    assert np.isfinite(shallow).all()
    assert not np.isfinite(deep[1])


def test_salinity_uses_its_own_threshold():
    depths = np.array([10.0, 20.0, 30.0])
    assert not np.isfinite(reject_spikes(depths, np.array([34.0, 35.2, 34.0]), "salinity")[1])
    assert np.isfinite(reject_spikes(depths, np.array([34.0, 34.8, 34.0]), "salinity")).all()


def test_the_end_levels_and_missing_neighbours_are_handled_without_guessing():
    """A spike needs a value above and below it. The top and bottom level cannot be tested and
    are kept, and a missing level is skipped over to the next real reading rather than read as
    a neighbour of zero."""
    depths = np.array([0.0, 10.0, 20.0, 30.0])
    temperature = np.array([0.0, 29.0, np.nan, 29.0])
    cleaned = reject_spikes(depths, temperature, "temperature")
    assert cleaned[0] == 0.0 and cleaned[1] == 29.0 and cleaned[3] == 29.0
    assert not np.isfinite(cleaned[2])


def test_the_parser_applies_the_spike_test():
    spiked = OMNI.replace(",20.0,29.09,33.72,", ",20.0,0.0,33.72,")
    profile = parse_osmc(spiked)[0]
    assert not np.isfinite(profile.values["temperature"][2])
    assert np.isfinite(profile.values["salinity"][2]), "only the channel that failed is refused"


def test_reports_are_thinned_to_one_a_day():
    """A moored buoy reports every three hours. Eight identical-looking casts a day is 80 per
    Timestep window per instrument, which is a fact about telemetry rather than about the ocean
    - the same trap `coverage.py` records for counting levels instead of casts."""
    profiles = thin_to_one_per_day(parse_osmc(OMNI))
    assert len(profiles) == 1
    assert profiles[0].time.hour == 0


def test_thinning_keeps_the_richest_report_of_the_day():
    thin = OMNI.replace(
        "23459,MOORED BUOYS (GENERIC),INDIA,2026-07-25T00:00:00Z,13.984,87.02,500.0,9.97,35.1,NaN,NaN\n",
        "",
    )
    profiles = thin_to_one_per_day(parse_osmc(thin))
    assert len(profiles) == 1
    assert len(profiles[0]) == 6, "the 03:00 report has more levels and should win"


def test_the_source_is_a_registered_provider_reading_its_own_dataset():
    source = OsmcSource()
    assert "OSMC_RealTime" in source.endpoint
    assert "public domain" in source.attribution.lower() or "cc0" in source.attribution.lower()
