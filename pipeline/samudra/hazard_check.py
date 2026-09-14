"""How close our hazard surfaces come to the ones INCOIS published, cell by cell.

`hazard.py` recomputes depth of the 26 degC and 20 degC isotherms, mixed layer depth and
isothermal layer depth for 2025-26 from INCOIS's Argo analysis, whose own series of them ended on
2019-03-30. (INCOIS still publish heat potential and mixed layer depth from their forecast models;
checked on incois.gov.in on 2026-09-13.) The
only external check such a recomputation can have is to run it over the years INCOIS *did*
publish and compare - `sources/incois_vap.py` reads their answer, `scripts/fetch_hazard_check.py`
computes ours from the same VAM analysis on the same dates, and this is the arithmetic.

**What the comparison found, and why the layer depths are reported twice.** Measured over 183
dates from 2004 to 2019 (`scripts/check_hazard_against_incois.py` prints the current figures):

- Depth of 26 degC is the same number as INCOIS's in 97.2% of 257,548 cells, and depth of 20 degC
  in 98.7% of 262,042. Where the two differ the gap is not small - a median 9.5 m and 6.9 m - and
  those cells are not concentrated in one region, so no cause is claimed for them.
- INCOIS's "Mixed Layer Depth" is **identical to their "Isothermal Layer Depth"** on every date,
  and both follow one rule: the depth where temperature falls **0.5 degC** below its 10 m value.
  Run with that rule, ours is the same number in 92.0% of cells. So INCOIS's MLD is a
  temperature criterion, not a density one.
- This platform follows de Boyer Montegut et al. (2004): 0.2 degC for the isothermal layer and
  0.03 kg/m3 of density for the mixed layer. Both are stricter, so ours read shallower.

A gap caused by choosing a different, published criterion is a **definition difference, not an
error**, and reporting it as disagreement would be exactly the kind of mistake this project is
careful to avoid. So each layer depth is reported against INCOIS with their rule (which is the
test of the code) and with ours (which is the size of the definition gap), and both are labelled.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

#: Two numbers closer than this are the same number. The published surfaces are float32, which
#: holds a depth near 100 m to about 0.00001 m, so this is generous and still means "identical".
EXACT_METRES = 0.05

#: The rule INCOIS's published MLD and ILD both follow: temperature 0.5 degC below its 10 m value.
#: Not documented on the dataset; found by trying 0.2, 0.5, 0.8 and 1.0 degC from 5 m and from
#: 10 m against four dates, where only this one reproduced them.
INCOIS_THRESHOLD = 0.5


@dataclass(frozen=True)
class Agreement:
    #: Cells where both sides had a value, pooled over every date.
    cells: int
    #: Share of those cells where the two are the same number, within `EXACT_METRES`.
    exact_share: float
    #: Median of |ours - theirs|, in metres.
    median_abs_metres: float
    #: Median of ours - theirs. Negative means ours is shallower.
    median_signed_metres: float
    #: Median of |ours - theirs| over the cells that are *not* exact. A 97% exact share reads as
    #: perfect, and the other 3% can still be tens of metres apart. NaN when every cell is exact.
    median_abs_where_different: float


def agreement(ours, theirs) -> Agreement:
    """Pool one date or many, cell by cell. `ours` and `theirs` are an array or a sequence of them.

    Only cells where both sides computed a value are compared. A cell one side left missing is
    neither agreement nor disagreement, so it is dropped and `cells` says how many were kept.
    """
    ours_list = _as_list(ours)
    theirs_list = _as_list(theirs)
    if len(ours_list) != len(theirs_list):
        raise ValueError("ours and theirs must hold the same number of dates")

    differences = []
    for mine, published in zip(ours_list, theirs_list):
        mine = np.asarray(mine, dtype=float)
        published = np.asarray(published, dtype=float)
        if mine.shape != published.shape:
            raise ValueError(f"shapes differ: {mine.shape} against {published.shape}")
        both = np.isfinite(mine) & np.isfinite(published)
        differences.append(mine[both] - published[both])

    pooled = np.concatenate(differences) if differences else np.array([])
    if pooled.size == 0:
        raise ValueError("no cell has a value on both sides, so there is nothing to compare")
    different = pooled[np.abs(pooled) > EXACT_METRES]
    return Agreement(
        cells=int(pooled.size),
        exact_share=float(np.mean(np.abs(pooled) <= EXACT_METRES)),
        median_abs_metres=float(np.median(np.abs(pooled))),
        median_signed_metres=float(np.median(pooled)),
        median_abs_where_different=float(np.median(np.abs(different))) if different.size else float("nan"),
    )


def _as_list(value) -> Sequence:
    if isinstance(value, np.ndarray):
        return [value]
    return list(value)
