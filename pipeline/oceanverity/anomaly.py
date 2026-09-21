"""Anomaly: how far this Timestep's water is from its own average, cell by cell.

Absolute temperature is dominated by geography. The Arabian Sea is warmer than the equatorial
Indian Ocean and 100 m is colder than the surface, and both are true in every frame, so an
absolute field spends its whole colour range restating the map. Subtracting each cell's own
average over time throws that away and leaves only what changed, which is the question a
forecaster is actually asking.

What the baseline is, and what it is not

**It is the mean of the Timesteps in this bake and nothing else.** However many ten-day steps
the bake fetched - the manifest's `timesteps` says how many and which - and no figure about the
window is written here, because this docstring said "twelve steps, April to July 2026" for a
round after the bake became a year.

It is **not** a climatology. "Warmer than normal" in the sense an operational centre means it -
warmer than the 1991-2020 average for this week of the year - would need a thirty-year
reference series and is not this Field. `climatology.py` and Temperature vs Normal are that
one, against the World Ocean Atlas; the two look identical on screen and mean completely
different things, so the guide panel says which one this is, in those words. Presenting the
mean of one bake as a thirty-year normal would be the same class of error as calling a z-score a
confidence.

What it does show honestly is the seasonal swing, and the departure is largest in the
thermocline rather than at the surface, because what moves is the thermocline. That claim is
**measured, not written here**: `spread_by_level` computes the per-Level spread, `bake.py`
writes it into the manifest as `anomalySpread`, and the guide panel quotes it through tokens.
This paragraph and the guide bullet carried two different sets of figures for the same
quantity - 0.74 / 1.55 / 0.08 degC here and 0.57 / 1.33 / 0.06 forty lines down - and neither was
the bake that shipped.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy import ndimage

from .grid import Grid

# The anomalies of a few cells are enormous - a thermocline that moved a long way vertically
# puts 24 degC of departure into a single cell - and a colour scale stretched to reach them
# would leave the entire ocean sitting in the middle two colours. Clipped, like every other
# Field's range, and stated rather than hidden.
_RANGE_PERCENTILE = 99.0

# A field that never moves still needs a drawable range. Half a degree is small enough that any
# real signal fills the bar and large enough that vmin never equals vmax.
_MINIMUM_HALF_RANGE = 0.5

METRES_PER_DEGREE = 111_320.0


def anomaly_series(grids: Sequence[Grid]) -> list[Grid]:
    """Each Grid's departure from the per-cell mean of all of them.

    Per cell, not per block: a permanently cold corner of the map is a cold corner, not an
    anomaly, and only its departure from its own average over time is one.

    Masked cells stay masked. The land mask is identical in every Timestep of this product, so
    a plain mean is safe, but NaN propagating is what keeps that true if it ever stops being.
    """
    grids = list(grids)
    if len(grids) < 2:
        raise ValueError(
            f"an anomaly needs at least two Timesteps to average, got {len(grids)}"
        )
    _require_same_axes(grids)

    stacked = np.stack([g.values for g in grids])
    baseline = stacked.mean(axis=0)

    return [
        Grid(
            levels=g.levels,
            latitudes=g.latitudes,
            longitudes=g.longitudes,
            values=g.values - baseline,
        )
        for g in grids
    ]


def symmetric_encoding_range(
    grids: Sequence[Grid], percentile: float = _RANGE_PERCENTILE
) -> tuple[float, float]:
    """An encoding range centred on zero, so a diverging palette's midpoint means what it says.

    Every other Field takes its range from the 0.5th and 99.5th percentiles of its own values.
    Doing that here would put zero somewhere other than the middle of the colourbar, and every
    colour either side of it would then be claiming the wrong sign.
    """
    finite = np.concatenate([g.values[np.isfinite(g.values)].ravel() for g in grids])
    reach = float(np.percentile(np.abs(finite), percentile)) if finite.size else 0.0
    reach = max(reach, _MINIMUM_HALF_RANGE)
    return -reach, reach


@dataclass(frozen=True)
class LevelSpread:
    """How much each Level moves across the series, and which Level moves most.

    `degrees[i]` is the median over that Level's ocean cells of the per-cell standard deviation
    across time. Median rather than mean because a handful of cells where the thermocline
    travelled a long way vertically carry tens of degrees of departure, and the same clipping
    argument `symmetric_encoding_range` makes applies to a summary figure.
    """

    metres: list[float]
    degrees: list[float]

    @property
    def peak_metres(self) -> float:
        return self.metres[int(np.argmax(self.degrees))]

    @property
    def peak_degrees(self) -> float:
        return self.degrees[int(np.argmax(self.degrees))]

    def at(self, metres: float) -> float:
        """The spread at the Level nearest `metres`. The Levels are uneven, so nearest is right."""
        index = int(np.argmin(np.abs(np.asarray(self.metres) - metres)))
        return self.degrees[index]


def spread_by_level(grids: Sequence[Grid]) -> LevelSpread:
    """How far each Level's water moves across the series, Level by Level.

    This is the sentence the guide panel makes about the Anomaly Field - *the signal is strongest
    in the thermocline, not at the surface* - turned into a measurement. It existed as a number
    typed into prose in two places with two different values for one quantity, and the value on
    screen was from a bake that no longer exists. A figure nothing computes cannot be checked by
    anything, so this computes it and `bake.py` writes it into the manifest.

    Masked cells stay out of it entirely rather than counting as calm water: land does not have
    a standard deviation of zero, it has none.
    """
    grids = list(grids)
    if len(grids) < 2:
        raise ValueError(
            f"a spread needs at least two Timesteps to vary between, got {len(grids)}"
        )
    _require_same_axes(grids)

    stacked = np.stack([g.values for g in grids])
    # Population rather than sample: this is the spread of the steps that are here, not an
    # estimate of a wider population, and there is no wider population - the baseline is these
    # steps and nothing else, which is what every sentence about this Field already says.
    deviation = np.std(stacked, axis=0, ddof=0)

    metres = [float(v) for v in grids[0].levels]
    degrees = []
    for level in range(deviation.shape[0]):
        ocean = deviation[level][np.isfinite(deviation[level])]
        degrees.append(float(np.median(ocean)) if ocean.size else 0.0)
    return LevelSpread(metres=metres, degrees=degrees)


def _require_same_axes(grids: Sequence[Grid]) -> None:
    first = grids[0]
    for name in ("levels", "latitudes", "longitudes"):
        for other in grids[1:]:
            if not np.array_equal(getattr(first, name), getattr(other, name)):
                raise ValueError(f"Timesteps disagree about {name}; they are not one series")


# ------------------------------------------------------------------ Anomaly Features
#
# A coloured field tells you *that* something departed. It does not tell you which blob you are
# looking at, how big it is, or whether to believe it. An Anomaly Feature is one connected body
# of water that departed, turned into something a user can click.
#
# Two thresholds, and it has to pass both.
#
# **Unusual.** The departure divided by how much that cell varies across the series - a z-score.
# A fixed threshold in degrees cannot work at every depth, because the per-cell spread is about
# twenty times larger in the thermocline than at 2000 m (`manifest.anomalySpread` has the whole
# profile): one number would find nothing but thermocline or nothing but noise. Measured on the
# 36-Timestep bake of 2026-09-09, |z| reaches 1.62 at the 90th percentile and 2.57 at the 99th,
# and 4.1% of ocean cells clear 2.0 - so 2.0 selects the top few per cent. It said 1.63 and
# 2.42 at twelve steps; the argument held and the figures moved.
#
# **Big enough to matter.** Half a degree. A hundredth of a degree in water that never moves is a
# huge z-score and a physically meaningless one, and the deep ocean is full of those. Surfacing
# one beside a 3 degC thermocline swing would be technically true and misleading.
#
# Together these give about eleven features per Timestep on the 36-step bake (404 in all),
# which is a number a person can actually work through. They are a presentation choice and are stated rather than
# hidden.
Z_THRESHOLD = 2.0
DEGREES_THRESHOLD = 0.5

# Below this a "feature" is a handful of cells and probably one noisy analysis point. Fifteen
# cells of a 1 degree grid is a few hundred kilometres across and a few Levels deep, which is
# mesoscale - the size of thing that has a name in oceanography.
MIN_CELLS = 15

# How many to keep per Timestep, strongest first.
DEFAULT_LIMIT = 12


@dataclass(frozen=True)
class AnomalyFeature:
    """One connected body of water that departed from its own average."""

    sign: int              # +1 warmer than usual, -1 cooler
    peak_value: float      # the departure at its strongest point, signed, in the Field's units
    peak_z: float          # how unusual that point is for its own cell, signed
    # Where the body *is*, not where it is strongest. The marker goes here and every fact the
    # panel reports is read from this cell, because a user who clicks a ring is asking about the
    # water under the ring. Placing it at the peak put it a median 222 km away, and 1063 km at
    # worst, so a ring could sit at one end of a long body describing water at the other.
    latitude: float
    longitude: float
    depth_metres: float
    top_metres: float      # the shallowest Level the body reaches
    bottom_metres: float
    south: float           # the box it occupies, for a marker and a rough size
    north: float
    west: float
    east: float
    cell_count: int
    # Horizontal area actually covered, counting each column once however deep it runs. This
    # replaced the span of the bounding box, which a diagonal or curved band inflates: one such
    # body reported 3228 km "across" from 705 cells.
    footprint_km2: float = 0.0
    # Where the marker sits in the Grid. Carried so anything describing this feature - the depth
    # of the isotherm here, what salinity did, how many casts are nearby - reads the *same* cell
    # rather than re-deriving it from the latitude and longitude and landing one over.
    centre_index: tuple[int, int, int] = (0, 0, 0)

    @property
    def strength(self) -> float:
        return abs(self.peak_value)


def find_anomaly_features(
    anomalies: Sequence[Grid],
    z_threshold: float = Z_THRESHOLD,
    value_threshold: float = DEGREES_THRESHOLD,
    min_cells: int = MIN_CELLS,
    limit: int = DEFAULT_LIMIT,
) -> list[list[AnomalyFeature]]:
    """Find the connected departures in each Timestep of an anomaly series.

    Warm and cool are labelled **separately**. Thresholding on the absolute departure merges a
    warm body into the cool one beside it wherever the front between them is sharp enough that
    no cell falls back inside the threshold, and on real data that produced a single "feature"
    spanning the entire basin and containing both +5.3 and -7.7 degC. See the test.
    """
    anomalies = list(anomalies)
    if not anomalies:
        return []

    stacked = np.stack([g.values for g in anomalies])
    spread = stacked.std(axis=0)
    # A cell that never moves has no scale to judge a departure against, and dividing by it
    # would manufacture an enormous z-score out of rounding.
    scores = np.divide(
        stacked, spread, out=np.full_like(stacked, np.nan), where=spread > 1e-6
    )

    return [
        _features_in(anomalies[t], scores[t], z_threshold, value_threshold, min_cells, limit)
        for t in range(len(anomalies))
    ]


def _features_in(grid, scores, z_threshold, value_threshold, min_cells, limit):
    found: list[AnomalyFeature] = []

    for sign in (1, -1):
        # NaN is land and must never pass a threshold, so it becomes zero rather than being
        # compared - a NaN comparison is False anyway, but being explicit keeps it that way.
        unusual = np.nan_to_num(sign * scores, nan=0.0) > z_threshold
        large = np.nan_to_num(sign * grid.values, nan=0.0) > value_threshold
        labels, count = ndimage.label(unusual & large)
        if count == 0:
            continue

        for label in range(1, count + 1):
            cells = labels == label
            size = int(cells.sum())
            if size < min_cells:
                continue
            found.append(_describe(grid, scores, cells, sign, size))

    found.sort(key=lambda f: f.strength, reverse=True)
    return found[:limit]


def _describe(grid, scores, cells, sign, size) -> AnomalyFeature:
    values = np.where(cells, grid.values, np.nan)
    peak = np.unravel_index(np.nanargmax(sign * values), values.shape)
    depths, rows, columns = np.where(cells)
    level, row, column = _centre_cell(depths, rows, columns)

    return AnomalyFeature(
        sign=sign,
        peak_value=float(grid.values[peak]),
        peak_z=float(scores[peak]),
        latitude=float(grid.latitudes[row]),
        longitude=float(grid.longitudes[column]),
        depth_metres=float(grid.levels[level]),
        top_metres=float(grid.levels[depths.min()]),
        bottom_metres=float(grid.levels[depths.max()]),
        south=float(grid.latitudes[rows.min()]),
        north=float(grid.latitudes[rows.max()]),
        west=float(grid.longitudes[columns.min()]),
        east=float(grid.longitudes[columns.max()]),
        cell_count=size,
        footprint_km2=_footprint(grid.latitudes, rows, columns),
        centre_index=(int(level), int(row), int(column)),
    )


def _centre_cell(depths, rows, columns):
    """The cell of the body nearest its own mass centre.

    Nearest rather than the mass centre itself, because a body can be a crescent or a shell and
    its centre of mass then falls in the hole. Reading salinity out of a hole would describe
    water that is not part of the feature at all.
    """
    centre = np.array([depths.mean(), rows.mean(), columns.mean()])
    occupied = np.stack([depths, rows, columns], axis=1).astype(float)
    nearest = int(np.argmin(np.square(occupied - centre).sum(axis=1)))
    return int(depths[nearest]), int(rows[nearest]), int(columns[nearest])


def _footprint(latitudes, rows, columns) -> float:
    """Area of the body's horizontal shadow, in square kilometres.

    Each column counts once however many Levels deep it runs, and each contributes the area of
    its own grid cell - which shrinks with latitude, because a degree of longitude does.
    """
    spacing = float(abs(latitudes[1] - latitudes[0])) if len(latitudes) > 1 else 1.0
    side = spacing * METRES_PER_DEGREE / 1000.0
    seen = {(int(r), int(c)) for r, c in zip(rows, columns)}
    return float(
        sum(side * side * np.cos(np.radians(latitudes[row])) for row, _ in seen)
    )
