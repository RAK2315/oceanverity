"""Compare our hazard surfaces with INCOIS's published ones, and write the result for the site.

Reads `data/hazard_check/*.npz`, written by `fetch_hazard_check.py`, and writes
`web/public/data/hazard_check.json`. A file of its own rather than a block in the manifest,
because a bake rewrites the manifest and this check is not part of a bake: it reads 2004-2019,
and the bake reads the last year.

Every figure the provenance page, the requirements page and `ppt/FACTS.md` quote about this
check comes from that file. See `samudra/hazard_check.py` for why the two layer depths are
reported twice.

    ../.venv/Scripts/python scripts/check_hazard_against_incois.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from samudra.hazard_check import EXACT_METRES, INCOIS_THRESHOLD, agreement  # noqa: E402
from samudra.hazard import TEMPERATURE_THRESHOLD, DENSITY_THRESHOLD  # noqa: E402
from samudra.sources.incois_vap import DATASET  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "data" / "hazard_check"
OUT = ROOT / "web" / "public" / "data" / "hazard_check.json"

#: (key, what is being compared, our array, INCOIS's array, which question it answers)
COMPARISONS = (
    ("d26", "Depth of 26 degC", "ours_d26", "theirs_d26", "code"),
    ("d20", "Depth of 20 degC", "ours_d20", "theirs_d20", "code"),
    (
        "isothermal_layer_depth",
        f"Isothermal layer depth, INCOIS's rule ({INCOIS_THRESHOLD} degC)",
        "ours_layer_depth_incois_rule",
        "theirs_isothermal_layer_depth",
        "code",
    ),
    (
        "mixed_layer_depth",
        f"Mixed layer depth, INCOIS's rule ({INCOIS_THRESHOLD} degC)",
        "ours_layer_depth_incois_rule",
        "theirs_mixed_layer_depth",
        "code",
    ),
    (
        "isothermal_layer_depth_platform_rule",
        f"Isothermal layer depth, this platform's rule ({TEMPERATURE_THRESHOLD} degC)",
        "ours_isothermal_layer_depth",
        "theirs_isothermal_layer_depth",
        "definition",
    ),
    (
        "mixed_layer_depth_platform_rule",
        f"Mixed layer depth, this platform's rule ({DENSITY_THRESHOLD} kg/m3 of density)",
        "ours_mixed_layer_depth",
        "theirs_mixed_layer_depth",
        "definition",
    ),
)


def main() -> int:
    files = sorted(CACHE.glob("*.npz"))
    if not files:
        print(f"nothing in {CACHE}; run fetch_hazard_check.py first", file=sys.stderr)
        return 1
    loaded = [dict(np.load(f)) for f in files]
    missing = [f.name for f, d in zip(files, loaded) if "ours_layer_depth_incois_rule" not in d]
    if missing:
        print(f"{len(missing)} cached dates predate the INCOIS-rule surface; delete and re-fetch", file=sys.stderr)
        return 1

    identical = sum(
        np.array_equal(d["theirs_mixed_layer_depth"], d["theirs_isothermal_layer_depth"], equal_nan=True)
        for d in loaded
    )

    results = []
    for key, label, mine, published, question in COMPARISONS:
        result = agreement([d[mine] for d in loaded], [d[published] for d in loaded])
        results.append(
            {
                "key": key,
                "label": label,
                "question": question,
                "cells": result.cells,
                "exactShare": round(result.exact_share, 4),
                "medianAbsMetres": round(result.median_abs_metres, 2),
                "medianSignedMetres": round(result.median_signed_metres, 2),
                "medianAbsWhereDifferentMetres": (
                    None if np.isnan(result.median_abs_where_different) else round(result.median_abs_where_different, 1)
                ),
            }
        )
        print(
            f"{label:<62} {result.cells:>7} cells  exact {result.exact_share:6.1%}  "
            f"median |diff| {result.median_abs_metres:6.2f} m  ours-theirs {result.median_signed_metres:+6.2f} m  "
            f"where different {result.median_abs_where_different:5.1f} m"
        )

    stamps = [f.stem for f in files]
    payload = {
        "generated": date.today().isoformat(),
        "dataset": DATASET,
        "dates": len(files),
        "first": stamps[0],
        "last": stamps[-1],
        "exactMetres": EXACT_METRES,
        "incoisRule": {"thresholdDegC": INCOIS_THRESHOLD, "referenceMetres": 10.0},
        # How many dates INCOIS's MLD and ILD were the same array. All of them is the finding
        # that their MLD is a temperature criterion.
        "incoisMldEqualsIld": {"dates": int(identical), "of": len(files)},
        "comparisons": results,
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"{len(files)} dates, {stamps[0]} to {stamps[-1]}; INCOIS MLD == ILD on {identical} -> {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
