"""Values no sea has ever held, masked at the door and counted.

INCOIS's temperature analysis carries cells that are not water. Measured over the 36-step bake of
2026-09-09: 1,221,804 ocean cells, of which 23 exceed 38 degC (the hottest 48.66 degC, at 30 m in
the Gulf of Oman) and 2 fall below -2.5 degC. Every one is on the region's northern edge, 24.5 to
25.5 N and 52.5 to 61.5 E - the Persian Gulf and the Gulf of Oman, where the analysis runs out of
open water. Most sit at 20 to 30 m, beneath a surface that should be the warmest water in the
column. None of them touched a Collocation.

The Volume never showed them, because every range is percentile-clipped. What did read them is
everything that reads the Grid: the tooltip, the section, and CF, OPeNDAP and WMS, which served
them exactly as published. A reader hovering the Gulf could have been told the sea was 45 degC.

**Masking a provider's numbers is a decision this project does not take lightly**, so three
things hold here, and `tests/test_plausibility.py` holds all three:

- **The bound is physical, with a source, never a percentile.** A percentile would mask the most
  extreme real water on every bake by construction.
- **A masked cell becomes Mask** - NaN, absence of ocean - never a clamped value, because a
  clamped 38 degC looks exactly like a measurement.
- **Every masked cell is counted**, and the bake writes the count and the bounds into the
  manifest, so the provenance page can say what was removed and why.

Why these bounds
----------------
The high bound is 38 degC because the verified in-situ record for the Persian Gulf - the hottest
sea on the planet - is 37.6 degC, in Kuwait Bay (Marine Pollution Bulletin, 2020, "World record
extreme sea surface temperatures in the northwestern Arabian/Persian Gulf verified by in situ
measurements"). A value above it is not a hot day; it is not water. The low bound is -2.5 degC,
below the freezing point of seawater at any salinity this region carries.

There is **no clean gap** between the real extremes and the faulty cells - the analysis runs
continuously from 35.8 through 36.1, 36.5 and 37.4 to 48.7 - so twelve cells between 36 and 38 degC
are suspicious, sit mostly below the surface, and are kept. A bound tighter than the record would
be a judgement about which hot water is real, and that is not this module's to make.
"""

from __future__ import annotations

import numpy as np

from .grid import Grid

#: Below seawater's freezing point; above the verified record for the hottest sea. See above.
TEMPERATURE_BOUNDS = (-2.5, 38.0)


def mask_implausible(grid: Grid, low: float, high: float) -> tuple[Grid, int]:
    """A copy of `grid` with every value outside [low, high] made Mask, and how many that was.

    Cells that were already Mask are neither counted nor changed. The input is left untouched,
    because a caller may still hold it, and a mask applied in place would hide the evidence of
    what was removed.
    """
    if not low < high:
        raise ValueError(f"bounds must be low < high, got {low} and {high}")
    values = np.array(grid.values, dtype=float, copy=True)
    outside = np.isfinite(values) & ((values < low) | (values > high))
    values[outside] = np.nan
    return (
        Grid(levels=grid.levels, latitudes=grid.latitudes, longitudes=grid.longitudes, values=values),
        int(outside.sum()),
    )
