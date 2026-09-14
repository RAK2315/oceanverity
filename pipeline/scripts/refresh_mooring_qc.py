"""Apply the moored-buoy spike test to the shipped bake, without re-fetching anything.

`sources/osmc.py` now runs Argo's spike test on every buoy report, because the range check alone
let a 0.0 degC reading at 20 m in the Bay of Bengal through and it moved the buoys' published
typical gap on its own. The bake that ships predates the test. Re-running a 36-Timestep bake to
apply it would re-fetch INCOIS, Argo, Copernicus and NOAA and move every other figure in the
build - to change a handful of buoy levels already on disk.

So this re-applies it the only honest way: every buoy comparison in `collocations.json` carries
the observed values the bake read, so `osmc.reject_spikes` - the parser's own function, not a
copy - is run over them, and any Timestep where a level fell is compared again through
`bake._collocate_cast` against `data/grids/*.npz`, the exact Grids that bake wrote. Then
`residuals.json` is rebuilt through `bake._build_residuals`. Argo floats are not touched: their
own quality flags already carry the spike test.

Before it writes anything it proves the reconstruction is faithful: every buoy step is compared
again **without** the test and must reproduce the shipped numbers, and the residuals rebuilt from
the untouched file must reproduce the shipped `residuals.json`. If either disagrees it stops.

**One difference from a real bake, stated rather than hidden.** A bake thins a buoy's eight
reports a day to the one with the most usable levels, *after* this test. Here the chosen report
is already fixed. A report that lost a level could, in a real bake, have lost the day to a
sibling report - so a real bake may pick a different report for that day. It cannot bring the
refused reading back.

    ../.venv/Scripts/python scripts/refresh_mooring_qc.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from samudra.bake import (  # noqa: E402
    DENSITY_FIELD,
    _build_residuals,
    _collocate_cast,
)
from samudra.grid import Grid  # noqa: E402
from samudra.sources.base import Profile  # noqa: E402
from samudra.sources.incois import IncoisErddapSource  # noqa: E402
from samudra.sources.osmc import reject_spikes  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "web" / "public" / "data"
GRIDS = ROOT / "data" / "grids"
CHANNELS = ("temperature", "salinity")


def load_grid(field: str, index: int) -> Grid:
    with np.load(GRIDS / f"{field}_{index:03d}.npz") as data:
        return Grid(
            levels=data["levels"],
            latitudes=data["latitudes"],
            longitudes=data["longitudes"],
            values=data["values"].astype(float),
        )


class LazyGrids(dict):
    """`grids[(field, index)]`, the shape `_collocate_cast` reads, loaded on first use."""

    def __missing__(self, key):
        self[key] = load_grid(*key)
        return self[key]


def as_array(values) -> np.ndarray:
    return np.array([np.nan if v is None else v for v in values], dtype=float)


def cast_from(step: dict, position: tuple[float, float], platform_id: str, qc: bool) -> Profile:
    """The report a buoy step was compared from, rebuilt from the observed values it carries."""
    fields = step["fields"]
    depths = np.array(fields["temperature"]["depths"], dtype=float)
    values = {}
    for channel in CHANNELS:
        block = fields.get(channel)
        if block is None:
            observed = np.full(len(depths), np.nan)
        else:
            if block["depths"] != fields["temperature"]["depths"]:
                raise SystemExit(f"{platform_id}: {channel} depths differ from temperature's")
            observed = as_array(block["observed"])
        values[channel] = reject_spikes(depths, observed, channel) if qc else observed
    latitude, longitude = position
    return Profile(
        platform_id=platform_id,
        latitude=latitude,
        longitude=longitude,
        time=datetime.fromisoformat(step["time"]),
        depths=depths,
        values=values,
        kind="mooring",
    )


def same(a, b) -> bool:
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


#: How far a re-comparison may sit from the shipped one. The bake stored positions to 4 decimal
#: places and values to 4, so rebuilding a cast from those moves the last digit and no more.
TOLERANCE = 5e-4


def close(a, b) -> bool:
    """Equal in shape, None and integer for integer, and within TOLERANCE for every float."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(close(x, y) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and abs(a - b) <= TOLERANCE
    return a == b


def main() -> int:
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    collocations = json.loads((DATA / "collocations.json").read_text(encoding="utf-8"))
    floats = json.loads((DATA / "floats.json").read_text(encoding="utf-8"))
    shipped_residuals = json.loads((DATA / "residuals.json").read_text(encoding="utf-8"))

    fields = [*IncoisErddapSource().fields(), DENSITY_FIELD]
    ranges = {f["key"]: tuple(f["range"]) for f in manifest["fields"] if f.get("range")}
    where = {(f["id"], fix["time"]): (fix["lat"], fix["lon"]) for f in floats for fix in f["track"]}
    grids = LazyGrids()

    # 1. The reconstruction must reproduce the bake before it is trusted to change anything.
    if not same(_build_residuals(collocations, floats, fields, ranges), shipped_residuals):
        print("residuals rebuilt from the shipped comparisons do not match residuals.json", file=sys.stderr)
        return 1

    refused: list[str] = []
    changed = json.loads(json.dumps(collocations))
    for platform_id, entry in collocations.items():
        if entry.get("kind") != "mooring":
            continue
        # A buoy swings a little on its mooring, so each report's own position is looked up in
        # the track by its time. Checked, not assumed: the untouched comparison must come back.
        steps = {}
        for key, step in entry["steps"].items():
            index = int(key)
            position = where[(platform_id, step["time"])]
            untouched = _collocate_cast(cast_from(step, position, platform_id, qc=False), grids, index, fields)
            if not close(untouched, step["fields"]):
                print(f"{platform_id} step {key}: re-comparison does not reproduce the bake", file=sys.stderr)
                return 1
            cast = cast_from(step, position, platform_id, qc=True)
            before = cast_from(step, position, platform_id, qc=False)
            for channel in CHANNELS:
                fell = np.isfinite(before.values[channel]) & ~np.isfinite(cast.values[channel])
                for depth, value in zip(cast.depths[fell], before.values[channel][fell]):
                    refused.append(f"{platform_id} step {key} {step['time'][:10]}: {channel} {value:g} at {depth:g} m")
            untouched_by_test = all(
                np.array_equal(cast.values[c], before.values[c], equal_nan=True) for c in CHANNELS
            )
            # A step the test did not touch keeps the bake's own numbers, byte for byte.
            got = step["fields"] if untouched_by_test else _collocate_cast(cast, grids, index, fields)
            if got:
                steps[key] = {"time": step["time"], "fields": got}
        if not steps:
            del changed[platform_id]
            continue
        newest = str(max(int(k) for k in steps))
        changed[platform_id] = {
            **entry,
            "timestepIndex": int(newest),
            "time": steps[newest]["time"],
            "fields": steps[newest]["fields"],
            "steps": steps,
        }

    residuals = _build_residuals(changed, floats, fields, ranges)
    print(f"{len(refused)} buoy readings refused by the spike test:")
    for line in refused:
        print(f"  {line}")
    for kind, block in residuals["fields"]["temperature"]["byKind"].items():
        old = shipped_residuals["fields"]["temperature"]["byKind"][kind]
        print(f"  temperature {kind}: typical gap {old['meanAbsBias']} -> {block['meanAbsBias']} degC over {block['count']}")

    (DATA / "collocations.json").write_text(json.dumps(changed), encoding="utf-8")
    (DATA / "residuals.json").write_text(json.dumps(residuals), encoding="utf-8")
    print("wrote collocations.json and residuals.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
