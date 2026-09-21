"""A named storm, and what the water it crossed did.

The platform shows a year of the ocean. A forecaster thinks in events, and Severe Cyclonic Storm
Montha crossed the Bay of Bengal inside this bake's window: 25 to 30 October 2025, landfall near
Narsapur on the evening of the 28th. This module holds the arithmetic a storm case needs and
nothing about how it is drawn.

**The track is IMD's, and nothing else.** It is read from the best track RSMC New Delhi publishes,
extracted into `data/storms/` with its source in the file's own header. A track traced off a news
map would be the one thing on screen this project could not source.

**Two things a storm case must not claim.**

- *That an instrument was under the storm.* Distance is measured to the track - the line between
  IMD's fixes - not to the nearest fix, and it is reported as a number. The two moored buoys that
  first looked "in the path" are 271 and 534 km from it.
- *That the storm caused a change.* The analyses are ten days apart, and between 20 and 30
  October the season moved too. So a change near the track is always set beside the change in
  water far from it, over the same two analyses, and the case says which it is.
"""

from __future__ import annotations

import csv
import io
import math
from dataclasses import dataclass
from datetime import datetime

import numpy as np

from .section import EARTH_RADIUS_KM, _initial_bearing, haversine_km


@dataclass(frozen=True)
class Fix:
    time: datetime
    latitude: float
    longitude: float
    #: IMD's grade: D, DD, CS, SCS and so on.
    grade: str
    wind_kt: float


def read_best_track(text: str) -> list[Fix]:
    """The committed extract: `#` comment lines, then `time_utc,latitude,longitude,grade,wind_kt`."""
    lines = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
    out = [
        Fix(
            time=datetime.fromisoformat(row["time_utc"].replace("Z", "+00:00")),
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            grade=row["grade"].strip(),
            wind_kt=float(row["wind_kt"]),
        )
        for row in csv.DictReader(io.StringIO("\n".join(lines)))
    ]
    out.sort(key=lambda f: f.time)
    return out


def distance_to_track_km(lon: float, lat: float, fixes: list[Fix]) -> float:
    """Great-circle distance from a point to the nearest point on the track, in kilometres.

    The track is the line between consecutive fixes. On each segment the spherical cross-track
    distance is used where the point projects inside it, and the distance to the nearer end
    where it does not - the same pair `section.casts_near_line` uses, so the two cannot disagree.
    """
    if not fixes:
        raise ValueError("a track needs at least one fix")
    best = min(haversine_km(lon, lat, f.longitude, f.latitude) for f in fixes)
    for a, b in zip(fixes, fixes[1:]):
        length = haversine_km(a.longitude, a.latitude, b.longitude, b.latitude)
        if length <= 0.0:
            continue
        angle = haversine_km(a.longitude, a.latitude, lon, lat) / EARTH_RADIUS_KM
        turn = _initial_bearing(a.longitude, a.latitude, lon, lat) - _initial_bearing(
            a.longitude, a.latitude, b.longitude, b.latitude
        )
        cross = math.asin(max(-1.0, min(1.0, math.sin(angle) * math.sin(turn))))
        along = math.acos(max(-1.0, min(1.0, math.cos(angle) / math.cos(cross))))
        if math.cos(turn) < 0.0:
            along = -along
        if 0.0 <= along * EARTH_RADIUS_KM <= length:
            best = min(best, abs(cross) * EARTH_RADIUS_KM)
    return best


@dataclass(frozen=True)
class Band:
    cells: int
    median_before: float
    median_after: float
    #: Share of cells whose value went up between the two analyses.
    share_increased: float


@dataclass(frozen=True)
class TrackChange:
    #: Cells within `near_km` of the track.
    near: Band
    #: Cells further than `far_km`, over the same two analyses - what the season did on its own.
    far: Band


def change_near_track(
    before: np.ndarray,
    after: np.ndarray,
    latitudes: np.ndarray,
    longitudes: np.ndarray,
    fixes: list[Fix],
    near_km: float,
    far_km: float,
) -> TrackChange:
    """One surface at two analyses, near the track against far from it.

    Only cells with a value at both analyses count. The gap between `near_km` and `far_km` is
    left out on purpose, so a cell at the edge of the storm's reach is not counted as either.
    """
    before = np.asarray(before, dtype=float)
    after = np.asarray(after, dtype=float)
    distance = np.array(
        [[distance_to_track_km(lon, lat, fixes) for lon in longitudes] for lat in latitudes]
    )
    both = np.isfinite(before) & np.isfinite(after)
    return TrackChange(
        near=_band(before, after, both & (distance <= near_km)),
        far=_band(before, after, both & (distance > far_km)),
    )


def _band(before: np.ndarray, after: np.ndarray, mask: np.ndarray) -> Band:
    if not mask.any():
        return Band(cells=0, median_before=math.nan, median_after=math.nan, share_increased=math.nan)
    return Band(
        cells=int(mask.sum()),
        median_before=float(np.median(before[mask])),
        median_after=float(np.median(after[mask])),
        share_increased=float(np.mean(after[mask] > before[mask])),
    )
