"""Save the World Ocean Atlas 2023 normal for this region, all twelve months, under `data/woa/`.

The bake reads these first and goes to NOAA only for a month that is missing, so Temperature vs
Normal survives NOAA's OPeNDAP server being down - which it was on 2026-09-14 and 2026-09-15. The
box is the analysis's own node bounds, read from a baked native Grid, exactly as `bake.py`
computes it, so a saved subset lines up with the analysis node for node.

    cd pipeline && ../.venv/Scripts/python scripts/fetch_woa_normals.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from samudra.sources.base import BoundingBox  # noqa: E402
from samudra.sources.woa import WoaClimatologySource  # noqa: E402

GRIDS = Path(__file__).resolve().parents[2] / "data" / "grids"


def main() -> None:
    with np.load(GRIDS / "temperature_000.npz") as grid:
        lats, lons = grid["latitudes"], grid["longitudes"]
    box = BoundingBox(south=float(lats[0]), north=float(lats[-1]), west=float(lons[0]), east=float(lons[-1]))
    source = WoaClimatologySource()
    for month in range(1, 13):
        normal = source.fetch_grid("temperature", month, box)
        print(
            f"month {month:02d}: {source.last_route}, {normal.values.shape}, "
            f"{np.isfinite(normal.values).mean():.0%} ocean",
            flush=True,
        )


if __name__ == "__main__":
    main()
