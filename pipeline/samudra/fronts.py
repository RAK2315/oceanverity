"""Surface fronts from satellite temperature and chlorophyll: the ingredient of a fishing advisory.

**What this is, and what it is not.** INCOIS's Potential Fishing Zone advisories are built from
fronts: edges where two bodies of surface water meet, which gather plankton and the fish that eat
it. INCOIS name their methods - Cayula and Cornillon (1992) for thermal fronts in sea surface
temperature, and Canny edge detection for chlorophyll fronts. This module follows both on
Copernicus satellite fields. **The result is a map of fronts, never a fishing zone**: INCOIS turn
fronts into advice with judgement, wind and their own validation, and none of that is here.

**Thermal fronts, after Cayula and Cornillon.** The field is cut into overlapping windows. In each,
the method asks whether the temperatures fall into two populations: the split that maximises the
between-population variance (Otsu's criterion) must explain at least `THETA` of the total variance,
the two means must differ by at least `MIN_STEP_DEGC`, and each population must be spatially
cohesive rather than salt-and-pepper. Where all three hold, the pixels where the two populations
touch are the front. The thresholds are the paper's where it gives one (0.76 and 0.92 cohesion);
the minimum contrast is ours, for a 0.05 degree analysis rather than 1 km imagery.

**Chlorophyll fronts, by Canny, on a log scale.** Chlorophyll spans three orders of magnitude and a
doubling is the same event at 0.05 and at 2 mg/m3, so the edge detector runs on log10. Gaussian
smoothing, Sobel gradient, thinning to the ridge, and hysteresis between two gradient thresholds.
The thresholds are ours, stated in decades per pixel.

**Onto the platform's grid.** A front is a line a few kilometres wide and the platform's cells are
about 110 km. So what reaches the platform is honest about that: for each 1 degree cell, the share
of its ocean pixels that sit on a front, thermal or chlorophyll. It is not upsampled into a line
finer than every other number the platform reports.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage

# ---- thermal (Cayula and Cornillon 1992) ------------------------------------------------------
WINDOW = 16          # pixels. 0.8 degree on a 0.05 degree analysis.
STRIDE = 8           # half-overlapping windows, as the paper does
THETA = 0.76        # share of the variance the two-population split must explain
COHESION = 0.92      # each population's same-population neighbour share
COHESION_ALL = 0.90  # the same, over both populations
MIN_STEP_DEGC = 0.4  # the two means must differ by at least this
MIN_OCEAN = 0.9      # a window this much land is not asked

# ---- chlorophyll (Canny) ----------------------------------------------------------------------
SIGMA = 1.0          # Gaussian smoothing, pixels
LOW_DECADES = 0.03   # hysteresis: weak edge, log10(mg/m3) per pixel
HIGH_DECADES = 0.06  # strong edge


def thermal_fronts(sst: np.ndarray) -> np.ndarray:
    """A boolean mask of thermal front pixels. NaN is land and is never a front."""
    sst = np.asarray(sst, dtype=float)
    rows, columns = sst.shape
    out = np.zeros(sst.shape, dtype=bool)
    for top in range(0, max(rows - WINDOW, 0) + 1, STRIDE):
        for left in range(0, max(columns - WINDOW, 0) + 1, STRIDE):
            window = sst[top : top + WINDOW, left : left + WINDOW]
            edge = _window_front(window)
            if edge is not None:
                out[top : top + WINDOW, left : left + WINDOW] |= edge
    return out


def _window_front(window: np.ndarray) -> np.ndarray | None:
    ocean = np.isfinite(window)
    if ocean.mean() < MIN_OCEAN:
        return None
    values = np.sort(window[ocean])
    n = values.size
    if n < 8 or values[-1] - values[0] < MIN_STEP_DEGC:
        return None

    # Otsu over every split of the sorted values.
    cumulative = np.cumsum(values)
    k = np.arange(1, n)
    below_mean = cumulative[:-1] / k
    above_mean = (cumulative[-1] - cumulative[:-1]) / (n - k)
    between = (k / n) * ((n - k) / n) * (below_mean - above_mean) ** 2
    total = values.var()
    if total <= 0:
        return None
    best = int(np.argmax(between))
    if between[best] / total < THETA:
        return None
    if above_mean[best] - below_mean[best] < MIN_STEP_DEGC:
        return None
    threshold = 0.5 * (values[best] + values[best + 1])

    warm = window > threshold
    # Neighbour pairs, right and down, where both pixels are ocean.
    pairs = []
    for a, b, both in (
        (warm[:, :-1], warm[:, 1:], ocean[:, :-1] & ocean[:, 1:]),
        (warm[:-1, :], warm[1:, :], ocean[:-1, :] & ocean[1:, :]),
    ):
        pairs.append((a, b, both))
    same_warm = sum(int((a & b & m).sum()) for a, b, m in pairs)
    same_cold = sum(int((~a & ~b & m).sum()) for a, b, m in pairs)
    mixed = sum(int(((a ^ b) & m).sum()) for a, b, m in pairs)
    if mixed == 0:
        return None
    c_warm = 2 * same_warm / (2 * same_warm + mixed)
    c_cold = 2 * same_cold / (2 * same_cold + mixed)
    c_all = (same_warm + same_cold) / (same_warm + same_cold + mixed)
    if min(c_warm, c_cold) < COHESION or c_all < COHESION_ALL:
        return None

    edge = np.zeros(window.shape, dtype=bool)
    (a, b, m), (c, d, n_) = pairs
    horizontal = (a ^ b) & m
    vertical = (c ^ d) & n_
    edge[:, :-1] |= horizontal
    edge[:, 1:] |= horizontal
    edge[:-1, :] |= vertical
    edge[1:, :] |= vertical
    return edge


def chlorophyll_fronts(chlorophyll: np.ndarray) -> np.ndarray:
    """A boolean mask of chlorophyll front pixels, by Canny on log10. NaN is land."""
    chl = np.asarray(chlorophyll, dtype=float)
    ocean = np.isfinite(chl) & (chl > 0)
    if not ocean.any():
        return np.zeros(chl.shape, dtype=bool)
    logged = np.where(ocean, np.log10(np.where(ocean, chl, 1.0)), 0.0)

    # Land must not be an edge. Fill it with the nearest ocean value before smoothing, so the
    # coast has no gradient of its own. Pixels near the coast are kept: a coastal bloom's edge is
    # exactly the front a fishing advisory is about.
    nearest = ndimage.distance_transform_edt(~ocean, return_distances=False, return_indices=True)
    filled = logged[tuple(nearest)]
    smooth = ndimage.gaussian_filter(filled, SIGMA)
    gx = ndimage.sobel(smooth, axis=1) / 8.0
    gy = ndimage.sobel(smooth, axis=0) / 8.0
    magnitude = np.hypot(gx, gy)

    thin = _non_maximum_suppression(magnitude, gx, gy)
    strong = thin & (magnitude >= HIGH_DECADES)
    weak = thin & (magnitude >= LOW_DECADES)
    labels, count = ndimage.label(weak, structure=np.ones((3, 3)))
    if count == 0:
        return np.zeros(chl.shape, dtype=bool)
    keep = np.zeros(count + 1, dtype=bool)
    keep[np.unique(labels[strong])] = True
    keep[0] = False
    edges = keep[labels]
    return edges & ocean


def _non_maximum_suppression(magnitude: np.ndarray, gx: np.ndarray, gy: np.ndarray) -> np.ndarray:
    """Keep a pixel only where it is the peak across the edge, in one of four directions."""
    angle = (np.rad2deg(np.arctan2(gy, gx)) + 180.0) % 180.0
    padded = np.pad(magnitude, 1, mode="edge")
    centre = padded[1:-1, 1:-1]
    neighbours = {
        0: (padded[1:-1, 2:], padded[1:-1, :-2]),
        45: (padded[2:, 2:], padded[:-2, :-2]),
        90: (padded[2:, 1:-1], padded[:-2, 1:-1]),
        135: (padded[2:, :-2], padded[:-2, 2:]),
    }
    direction = (np.round(angle / 45.0) * 45.0) % 180.0
    keep = np.zeros(magnitude.shape, dtype=bool)
    for degrees, (one, other) in neighbours.items():
        chosen = direction == degrees
        keep |= chosen & (centre >= one) & (centre >= other)
    return keep & (magnitude > 0)


def front_share(
    fronts: np.ndarray,
    ocean: np.ndarray,
    fine_latitudes: np.ndarray,
    fine_longitudes: np.ndarray,
    latitudes: np.ndarray,
    longitudes: np.ndarray,
) -> np.ndarray:
    """Percent of each platform cell's ocean pixels that lie on a front. NaN where no ocean.

    Cells are centred on `latitudes` and `longitudes`, one degree wide, the Grid's own nodes.
    """
    rows = np.searchsorted(latitudes - 0.5, fine_latitudes, side="right") - 1
    columns = np.searchsorted(longitudes - 0.5, fine_longitudes, side="right") - 1
    valid_rows = (rows >= 0) & (rows < latitudes.size) & (np.abs(fine_latitudes - latitudes[np.clip(rows, 0, latitudes.size - 1)]) <= 0.5)
    valid_columns = (columns >= 0) & (columns < longitudes.size) & (np.abs(fine_longitudes - longitudes[np.clip(columns, 0, longitudes.size - 1)]) <= 0.5)

    r, c = np.meshgrid(rows, columns, indexing="ij")
    inside = np.outer(valid_rows, valid_columns) & np.asarray(ocean, dtype=bool)
    on_front = inside & np.asarray(fronts, dtype=bool)

    ocean_count = np.zeros((latitudes.size, longitudes.size))
    front_count = np.zeros((latitudes.size, longitudes.size))
    np.add.at(ocean_count, (r[inside], c[inside]), 1)
    np.add.at(front_count, (r[on_front], c[on_front]), 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        share = 100.0 * front_count / ocean_count
    share[ocean_count == 0] = np.nan
    return share


def onto_grid(
    mask: np.ndarray,
    fine_latitudes: np.ndarray,
    fine_longitudes: np.ndarray,
    latitudes: np.ndarray,
    longitudes: np.ndarray,
) -> np.ndarray:
    """A front mask moved onto another regular pixel grid, keeping every front pixel.

    Each true pixel marks the target pixel whose footprint contains its centre. Used to put the
    1/24 degree chlorophyll fronts onto the 1/20 degree temperature grid, so the two can be joined
    into one mask. Nearest-neighbour sampling the other way would skip about one fine column in six
    and drop a thin edge that fell between samples.
    """
    lat_step = float(latitudes[1] - latitudes[0]) if latitudes.size > 1 else 1.0
    lon_step = float(longitudes[1] - longitudes[0]) if longitudes.size > 1 else 1.0
    rows, columns = np.nonzero(np.asarray(mask, dtype=bool))
    target_rows = np.floor((fine_latitudes[rows] - (latitudes[0] - lat_step / 2)) / lat_step).astype(int)
    target_columns = np.floor((fine_longitudes[columns] - (longitudes[0] - lon_step / 2)) / lon_step).astype(int)
    inside = (
        (target_rows >= 0) & (target_rows < latitudes.size)
        & (target_columns >= 0) & (target_columns < longitudes.size)
    )
    out = np.zeros((latitudes.size, longitudes.size), dtype=bool)
    out[target_rows[inside], target_columns[inside]] = True
    return out
