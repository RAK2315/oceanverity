"""Write `web/public/data/cases/montha.json`: what the platform can say about Cyclone Montha.

Every figure the storm walkthrough shows comes from this file, and every figure in this file is
measured here from data already in the build - IMD's track in `data/storms/`, the native Grids
in `data/grids/`, the buoy comparisons in `collocations.json` and the float fixes in
`floats.json`. Nothing is fetched and nothing is typed into the frontend, which is the rule
`guide.ts` already follows with its `{token}`s.

See `oceanverity/storm.py` for the two things a storm case must not claim, and why every change near
the track is set beside the change far from it.

    ../.venv/Scripts/python scripts/build_montha_case.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from oceanverity.grid import Grid  # noqa: E402
from oceanverity.hazard import depth_of_26, heat_potential, mixed_layer_depth  # noqa: E402
from oceanverity.drift import CurrentSeries, integrate_drift  # noqa: E402
from oceanverity.section import haversine_km  # noqa: E402
from oceanverity.storm import change_near_track, distance_to_track_km, read_best_track  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "web" / "public" / "data"
GRIDS = ROOT / "data" / "grids"
TRACK = ROOT / "data" / "storms" / "imd_best_track_montha_2025.csv"
OUT = DATA / "cases" / "montha.json"

#: Within this of the track is "near". 150 km is the corridor the section already uses for casts.
NEAR_KM = 150.0
#: Beyond this is "far": the same two analyses, water the storm did not reach.
FAR_KM = 500.0
#: Far water is taken from the Bay of Bengal only, so the comparison is the same sea in the same
#: season rather than the Arabian Sea, which runs a different monsoon cycle.
BAY = {"west": 78.0, "east": 100.0, "south": 5.0, "north": 23.0}
#: Instruments listed in the case: moorings in the Bay, floats that surfaced this close to the
#: track while the storm was in the water, give or take this many days.
FLOAT_KM = 300.0
FLOAT_DAYS = 3.0
#: How far the walkthrough's drift pin runs: one Argo cycle, the span the drift score covers.
DRIFT_DAYS = 10.0


def load(field: str, index: int) -> Grid:
    with np.load(GRIDS / f"{field}_{index:03d}.npz") as data:
        return Grid(
            levels=data["levels"],
            latitudes=data["latitudes"],
            longitudes=data["longitudes"],
            values=data["values"].astype(float),
        )


def in_bay(grid: Grid, surface: np.ndarray) -> np.ndarray:
    """The surface with everything outside the Bay made missing, so it is in neither band."""
    lat = np.asarray(grid.latitudes)[:, None]
    lon = np.asarray(grid.longitudes)[None, :]
    inside = (lat >= BAY["south"]) & (lat <= BAY["north"]) & (lon >= BAY["west"]) & (lon <= BAY["east"])
    return np.where(inside, surface, np.nan)


def band(result) -> dict:
    def one(b):
        return {
            "cells": b.cells,
            "medianBefore": round(b.median_before, 2),
            "medianAfter": round(b.median_after, 2),
            "shareIncreased": round(b.share_increased, 3),
        }

    return {"near": one(result.near), "far": one(result.far)}


def main() -> int:
    text = TRACK.read_text(encoding="utf-8")
    fixes = read_best_track(text)
    landfall_note = next(line for line in text.splitlines() if "Crossed" in line)
    found = re.search(r"latitude ([\d.]+)N and longitude ([\d.]+) ?E", landfall_note)
    place = re.search(r"close to (\w+)", landfall_note)
    when = re.search(r"UTC of (\d+)\w* (\w+)", landfall_note)
    landfall = {
        "lat": float(found.group(1)),
        "lon": float(found.group(2)),
        "place": place.group(1),
        "day": f"{int(when.group(1))} {when.group(2)}",
        "note": landfall_note.split(": ", 1)[1],
    }

    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    stamps = [datetime.fromisoformat(t) for t in manifest["timesteps"]]
    # The last analysis before the storm formed and the first after IMD stopped tracking it.
    before = max(i for i, t in enumerate(stamps) if t <= fixes[0].time)
    after = min(i for i, t in enumerate(stamps) if t >= fixes[-1].time)

    t0, t1 = load("temperature", before), load("temperature", after)
    d0, d1 = load("density", before), load("density", after)
    surfaces = {
        "mixedLayerDepth": (mixed_layer_depth(d0), mixed_layer_depth(d1), "m"),
        "d26": (depth_of_26(t0), depth_of_26(t1), "m"),
        "heatPotential": (heat_potential(t0), heat_potential(t1), "kJ/cm2"),
        # The analysis at its shallowest Level, 5 m: the cold wake, if the analysis saw one.
        "temperature5m": (t0.values[0], t1.values[0], "degC"),
    }
    changes = {}
    for key, (a, b, units) in surfaces.items():
        result = change_near_track(
            in_bay(t0, a), in_bay(t0, b), t0.latitudes, t0.longitudes, fixes, NEAR_KM, FAR_KM
        )
        changes[key] = {"units": units, **band(result)}
    # Which Level "the surface" is, so the card never types it.
    changes["temperature5m"]["depthMetres"] = float(t0.levels[0])

    # Where the walkthrough drops its drift pin: the water node nearest the landfall from which
    # the drift model actually runs the full ten days at the shallowest Level. Measured with
    # `drift.integrate_drift`, the tested integrator the browser's copy is checked against. The
    # nearest node with a current under it was not enough: 82.5 E, 16.5 N has one and still
    # refuses to start, because the integrator will not blend across the coast beside it - and a
    # pin that draws nothing is a walkthrough step that shows nothing.
    volume = manifest["volume"]
    shape = (len(volume["levelMetres"]), volume["height"], volume["width"], 2)
    axes = dict(levels=t1.levels, latitudes=t1.latitudes, longitudes=t1.longitudes)
    us, vs = [], []
    for name in manifest["currents"]["files"]:
        pair = np.fromfile(DATA / name, dtype="<f4").reshape(shape).astype(float)
        us.append(Grid(values=pair[..., 0], **axes))
        vs.append(Grid(values=pair[..., 1], **axes))
    series = CurrentSeries(times=stamps, u=us, v=vs)
    depth = float(t1.levels[0])
    candidates = sorted(
        (haversine_km(float(lon), float(lat), landfall["lon"], landfall["lat"]), float(lon), float(lat))
        for lat in t1.latitudes
        for lon in t1.longitudes
    )
    drift_pin = None
    for km, lon, lat in candidates[:200]:
        path = integrate_drift(series, lon, lat, stamps[after], depth, DRIFT_DAYS * 24.0)
        if path.ended == "finished":
            drift_pin = {"lon": lon, "lat": lat, "kmFromLandfall": round(km), "days": DRIFT_DAYS}
            break

    # Moored buoys in the Bay with a comparison at both analyses.
    collocations = json.loads((DATA / "collocations.json").read_text(encoding="utf-8"))
    floats = json.loads((DATA / "floats.json").read_text(encoding="utf-8"))
    where = {f["id"]: f for f in floats}
    buoys = []
    for platform_id, entry in collocations.items():
        if entry.get("kind") != "mooring":
            continue
        pair = [entry["steps"].get(str(before)), entry["steps"].get(str(after))]
        if not all(pair):
            continue
        lat, lon = where[platform_id]["latest"]["lat"], where[platform_id]["latest"]["lon"]
        if not (BAY["south"] <= lat <= BAY["north"] and BAY["west"] <= lon <= BAY["east"]):
            continue
        a, b = (p["fields"]["temperature"] for p in pair)
        # The shallowest depth both reports compared against the model at.
        shared = [
            d
            for d, m in zip(a["depths"], a["modelled"])
            if m is not None and d in b["depths"] and b["modelled"][b["depths"].index(d)] is not None
            and a["observed"][a["depths"].index(d)] is not None and b["observed"][b["depths"].index(d)] is not None
        ]
        if not shared:
            continue
        depth = min(shared)
        ia, ib = a["depths"].index(depth), b["depths"].index(depth)
        buoys.append(
            {
                "id": platform_id,
                "lat": lat,
                "lon": lon,
                "distanceKm": round(distance_to_track_km(lon, lat, fixes)),
                "depthMetres": depth,
                "measuredChange": round(b["observed"][ib] - a["observed"][ia], 2),
                "analysedChange": round(b["modelled"][ib] - a["modelled"][ia], 2),
                "reportTimes": [pair[0]["time"], pair[1]["time"]],
            }
        )
    buoys.sort(key=lambda b: b["distanceKm"])

    # Floats that surfaced near the track while the storm was in the water. Their comparison
    # charts are from their newest cast, not from October, and the case says so.
    start, end = fixes[0].time - timedelta(days=FLOAT_DAYS), fixes[-1].time + timedelta(days=FLOAT_DAYS)
    near_floats = []
    for f in floats:
        if f.get("kind") != "float":
            continue
        close = [
            (distance_to_track_km(fix["lon"], fix["lat"], fixes), fix)
            for fix in f["track"]
            if start <= datetime.fromisoformat(fix["time"]) <= end
        ]
        close = [c for c in close if c[0] <= FLOAT_KM]
        if close:
            km, fix = min(close, key=lambda c: c[0])
            near_floats.append({"id": f["id"], "distanceKm": round(km), "time": fix["time"], "lat": fix["lat"], "lon": fix["lon"]})
    near_floats.sort(key=lambda f: f["distanceKm"])

    payload = {
        "id": "montha",
        "name": "Montha",
        "grade": "Severe Cyclonic Storm",
        "basin": "Bay of Bengal",
        "source": {
            "who": "India Meteorological Department, RSMC New Delhi",
            "what": "Best Tracks Data (1982-2026), sheet 2025",
            "url": "https://rsmcnewdelhi.imd.gov.in/report.php?internal_menu=MzM=",
            "file": str(TRACK.relative_to(ROOT)).replace("\\", "/"),
        },
        "track": [
            {"time": f.time.isoformat(), "lat": f.latitude, "lon": f.longitude, "grade": f.grade, "windKt": f.wind_kt}
            for f in fixes
        ],
        "peakWindKt": max(f.wind_kt for f in fixes),
        "formed": fixes[0].time.isoformat(),
        "lastFix": fixes[-1].time.isoformat(),
        "landfall": landfall,
        "steps": {"before": before, "after": after, "beforeTime": manifest["timesteps"][before], "afterTime": manifest["timesteps"][after]},
        "method": {"nearKm": NEAR_KM, "farKm": FAR_KM, "bay": BAY, "floatKm": FLOAT_KM, "floatDays": FLOAT_DAYS},
        "changes": changes,
        "buoys": buoys,
        "floats": near_floats,
        "driftPin": drift_pin,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")

    print(f"steps {before} ({manifest['timesteps'][before][:10]}) -> {after} ({manifest['timesteps'][after][:10]})")
    for key, c in changes.items():
        n, f = c["near"], c["far"]
        print(f"  {key:<16} near {n['medianBefore']:>7} -> {n['medianAfter']:>7} ({n['cells']} cells, {n['shareIncreased']:.0%} up)"
              f"   far {f['medianBefore']:>7} -> {f['medianAfter']:>7} ({f['cells']} cells, {f['shareIncreased']:.0%} up)")
    for b in buoys:
        print(f"  buoy {b['id']:<8} {b['distanceKm']:>4} km  at {b['depthMetres']} m: measured {b['measuredChange']:+}, analysed {b['analysedChange']:+}")
    print(f"  {len(near_floats)} floats within {FLOAT_KM:.0f} km: " + ", ".join(f"{f['id']} {f['distanceKm']} km" for f in near_floats[:8]))
    print(f"  drift pin {drift_pin}")
    print(f"-> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
