"""Fill the shipped manifest's `anomalySpread` block from the native Grids the bake wrote.

`bake.py` writes this block now. The bake that ships predates it, and re-running a 36-Timestep
bake to add a derived figure would re-fetch INCOIS, Argo, Copernicus and NOAA and move every
other number in the build - to compute something that is a pure function of data already on
disk.

So this recomputes it the only honest way: it loads `data/grids/temperature_*.npz`, which are
the exact Grids that bake wrote, and hands them to `anomaly.spread_by_level` - the same
function `bake.py` calls, not a second implementation of it. Running the real bake afterwards
produces the same block.

Generated data stays generated, written by the pipeline, never hand-edited. Same standing as
`refresh_palettes.py` and `refresh_field_prose.py`.

    ../.venv/Scripts/python scripts/refresh_anomaly_spread.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from samudra.anomaly import spread_by_level  # noqa: E402
from samudra.bake import _spread_block  # noqa: E402
from samudra.grid import Grid  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "web" / "public" / "data" / "manifest.json"
GRIDS = ROOT / "data" / "grids"


def load_series(field: str, steps: int) -> list[Grid]:
    out = []
    for index in range(steps):
        path = GRIDS / f"{field}_{index:03d}.npz"
        if not path.exists():
            raise SystemExit(f"no {path.name}; run the bake with a --grids directory first")
        with np.load(path) as data:
            out.append(
                Grid(
                    levels=data["levels"],
                    latitudes=data["latitudes"],
                    longitudes=data["longitudes"],
                    values=data["values"].astype(float),
                )
            )
    return out


def main() -> int:
    if not MANIFEST.exists():
        print(f"no manifest at {MANIFEST}", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    steps = len(manifest["timesteps"])
    spread = spread_by_level(load_series("temperature", steps))
    block = _spread_block(spread)

    before = manifest.get("anomalySpread")
    manifest["anomalySpread"] = block
    MANIFEST.write_text(json.dumps(manifest), encoding="utf-8")

    verb = "unchanged" if before == block else ("added" if before is None else "rewritten")
    print(f"anomalySpread {verb} from {steps} native temperature Grids")
    print(f"  peak {block['peakDegC']:.2f} degC at {block['peakMetres']:.0f} m")
    print(f"  surface {spread.at(5.0):.2f} degC, 2000 m {spread.at(2000.0):.2f} degC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
