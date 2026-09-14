"""INCOIS's own Value Added Products: the hazard quantities they published, and then stopped.

`incois_valueadded_products_datasets` on INCOIS's public ERDDAP carries mixed layer depth,
isothermal layer depth, depth of the 26 degC and 20 degC isotherms, heat content to 300 m,
dynamic height and geostrophic currents, ten-daily, **2004-01-10 to 2019-03-30** - 549 steps,
measured on 2026-09-13. Every variable says `history: From VAM4m2004`, which is to say it was
derived from the VAM analysis `sources/incois.py` already reads, and its grid is the same one:
1 degree, node centres on the half degree, so the demo region is a straight subset with no
regridding. All 549 of its dates are dates in the VAM series.

That makes it the one external check this project's hazard Fields can have. `hazard.py`
recomputes these quantities for 2025-26, after this series stopped; run over the years it covers,
the recomputation can be held against the answer INCOIS gave. INCOIS still publish heat potential
and mixed layer depth from their forecast models (incois.gov.in/site/services/tchp.jsp, checked
2026-09-13) - it is this Argo-analysis series that ended.

What this adapter deliberately does not offer:

- **`HTCNT`** is heat content from the surface to 300 m, `x 1e-8 J/m2`. Cyclone heat potential is
  the Leipper-Volgenau integral of the excess over 26 degC down to the 26 degC isotherm. They are
  different quantities and comparing them would be wrong, so it is not read.
- **`DYN_HT`, `GEO_U`, `GEO_V`** have no counterpart in the platform (ADR 0010 records why a
  derived geostrophic current was rejected).

It is a check, not a Field: nothing here reaches the Variable selector, because a 2019 value
drawn on a 2026 Timestep would be an observation that does not exist.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from functools import lru_cache
from typing import Sequence

import numpy as np
import requests
import xarray as xr

from ..tls import ca_bundle
from .base import BoundingBox

_SERVER = "https://erddap.incois.gov.in/erddap/griddap"
_TIMEOUT = 120

DATASET = "incois_valueadded_products_datasets"

#: The platform's name for each quantity, and INCOIS's.
VARIABLES = {
    "mixed_layer_depth": "MLD",
    "isothermal_layer_depth": "ILD",
    "d26": "D26",
    "d20": "D20",
}


class IncoisValueAddedSource:
    """Reads INCOIS's published hazard surfaces, for checking ours against."""

    name = "INCOIS ERDDAP (Value Added Products)"
    attribution = (
        "Indian National Centre for Ocean Information Services (INCOIS), Ministry of Earth "
        "Sciences - Value Added Products from the VAM Argo analysis, 2004 to 2019"
    )
    dataset = DATASET
    endpoint = f"erddap.incois.gov.in/erddap/griddap/{DATASET}"

    def timesteps(self) -> Sequence[datetime]:
        return _fetch_timesteps(self.dataset)

    def fetch_surfaces(
        self, timestep: datetime, bbox: BoundingBox
    ) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
        """Latitudes, longitudes and every quantity in `VARIABLES` at one step, in metres."""
        stamp = timestep.strftime("%Y-%m-%dT%H:%M:%SZ")
        window = f"[({stamp})][({bbox.south}):({bbox.north})][({bbox.west}):({bbox.east})]"
        selector = ",".join(f"{name}{window}" for name in VARIABLES.values())
        response = requests.get(
            f"{_SERVER}/{self.dataset}.nc?{selector}", timeout=_TIMEOUT, verify=ca_bundle()
        )
        response.raise_for_status()
        return parse_surfaces(response.content)


def parse_surfaces(payload: bytes) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    """The NetCDF ERDDAP returns, as plain arrays keyed by the platform's own names."""
    with xr.open_dataset(io.BytesIO(payload)) as ds:
        latitudes = ds["latitude"].values.astype(float)
        longitudes = ds["longitude"].values.astype(float)
        surfaces = {
            key: ds[name].isel(time=0).values.astype(float)
            for key, name in VARIABLES.items()
            if name in ds
        }
    return latitudes, longitudes, surfaces


@lru_cache(maxsize=1)
def _fetch_timesteps(dataset: str) -> tuple[datetime, ...]:
    response = requests.get(f"{_SERVER}/{dataset}.json?time", timeout=_TIMEOUT, verify=ca_bundle())
    response.raise_for_status()
    return tuple(
        datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        for row in response.json()["table"]["rows"]
    )
