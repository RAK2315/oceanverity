"""Fetch what the hazard check compares: INCOIS's published surfaces, and ours for the same days.

For every sampled date in INCOIS's Value Added Products (2004-2019), this reads the VAM
temperature and salinity for that date, runs them through exactly the chain `bake.py` runs -
`plausibility.mask_implausible`, `density.potential_density`, then `hazard.py` and
`thermocline.isotherm_depth` - and stores our surfaces beside INCOIS's own in one small file per
date under `data/hazard_check/`. Those files are committed, like the glider index, so the
comparison is reproducible without the download.

`scripts/check_hazard_against_incois.py` does the comparison. This only fetches, because a
download that dies half way should not leave a half-written figure behind.

    ../.venv/Scripts/python scripts/fetch_hazard_check.py            # every 3rd step, 183 dates
    ../.venv/Scripts/python scripts/fetch_hazard_check.py --every 1  # all 549

Already-fetched dates are skipped, so it can be stopped and re-run.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from oceanverity.bake import DEMO_REGION  # noqa: E402
from oceanverity.density import potential_density  # noqa: E402
from oceanverity.hazard import depth_of_26, isothermal_layer_depth, mixed_layer_depth  # noqa: E402
from oceanverity.hazard_check import INCOIS_THRESHOLD  # noqa: E402
from oceanverity.plausibility import TEMPERATURE_BOUNDS, mask_implausible  # noqa: E402
from oceanverity.sources.incois import IncoisErddapSource  # noqa: E402
from oceanverity.sources.incois_vap import IncoisValueAddedSource  # noqa: E402
from oceanverity.thermocline import isotherm_depth  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "hazard_check"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--every", type=int, default=3, help="take every Nth published date")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    theirs = IncoisValueAddedSource()
    model = IncoisErddapSource()
    dates = list(theirs.timesteps())[:: args.every]
    print(f"{len(dates)} dates, {dates[0]:%Y-%m-%d} to {dates[-1]:%Y-%m-%d}", flush=True)

    for number, stamp in enumerate(dates, 1):
        path = OUT / f"{stamp:%Y-%m-%d}.npz"
        if path.exists():
            continue
        for attempt in range(3):
            try:
                latitudes, longitudes, published = theirs.fetch_surfaces(stamp, DEMO_REGION)
                temperature = model.fetch_grid("temperature", stamp, DEMO_REGION)
                salinity = model.fetch_grid("salinity", stamp, DEMO_REGION)
                break
            except Exception as error:  # a flaky link is not a reason to lose the run
                print(f"  {stamp:%Y-%m-%d} attempt {attempt + 1} failed: {error}", flush=True)
                time.sleep(5)
        else:
            continue

        if not (
            np.allclose(temperature.latitudes, latitudes) and np.allclose(temperature.longitudes, longitudes)
        ):
            # The whole check rests on the two datasets sharing node centres. Refuse, never regrid.
            print(f"  {stamp:%Y-%m-%d}: axes differ between VAM and the value added products", flush=True)
            return 1

        temperature, masked = mask_implausible(temperature, *TEMPERATURE_BOUNDS)
        density = potential_density(temperature, salinity)
        ours = {
            "mixed_layer_depth": mixed_layer_depth(density),
            "isothermal_layer_depth": isothermal_layer_depth(temperature),
            # INCOIS's own rule, found by reproducing their numbers. See `hazard_check.py`.
            "layer_depth_incois_rule": isothermal_layer_depth(temperature, threshold=INCOIS_THRESHOLD),
            "d26": depth_of_26(temperature),
            "d20": isotherm_depth(temperature, 20.0),
        }
        np.savez_compressed(
            path,
            latitudes=latitudes,
            longitudes=longitudes,
            masked=masked,
            **{f"ours_{k}": v.astype(np.float32) for k, v in ours.items()},
            **{f"theirs_{k}": v.astype(np.float32) for k, v in published.items()},
        )
        print(f"  [{number}/{len(dates)}] {stamp:%Y-%m-%d}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
