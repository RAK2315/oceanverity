"""Where fish can live in the water column, from quantities already on the Grid.

One quantity so far: the **oxygen floor**, the depth at which dissolved oxygen first falls below
2 mg/L on the way down from the surface. Below it the water is hypoxic, and most fish that INCOIS's
fishing advisories are about avoid it. In the Arabian Sea this floor sits high, because the region
holds one of the largest low-oxygen layers in the world ocean, so the same surface advisory can sit
over very different depths of usable water.

It is a **depth**, so it is drawn as a Sheet inside the block, exactly like the 26 degC isotherm
(ADR 0014), and it ships as float32 on the Grid rather than as a Volume, because a reader reads
metres off it.

**The limitation is the one `hazard.py` states.** The crossing is found between the model's Levels,
which are 25 m apart between 50 and 150 m, where this floor usually is. It is also computed from a
model's oxygen, not from measurements: the July 2026 check against BGC-Argo floats found the model
holding too much oxygen at 100-150 m, which would put this floor too deep. The bias map publishes
that gap for the bake's own window.
"""

from __future__ import annotations

import numpy as np

from .grid import Grid
from .thermocline import isotherm_depth

#: 2 mg/L of O2, at 32 g/mol, in the model's units. The conventional line for hypoxic water.
OXYGEN_FLOOR_MMOL = 2.0 / 32.0 * 1000.0


def oxygen_floor(oxygen: Grid, threshold: float = OXYGEN_FLOOR_MMOL) -> np.ndarray:
    """Depth in metres where oxygen first drops below `threshold`, read from the surface down.

    NaN where the column never drops below it within the Levels held, and over land. The crossing
    is the same first-crossing walk `thermocline.isotherm_depth` makes for a temperature, because
    it is the same question about a quantity that falls with depth.
    """
    return isotherm_depth(oxygen, threshold)
