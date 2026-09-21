"""Source Adapter for Copernicus Marine's global biogeochemical analysis: chlorophyll and oxygen.

**Why these two.** INCOIS's Potential Fishing Zone advisories are built from satellite sea surface
temperature and chlorophyll, and INCOIS's own staff name clouds in the monsoon as the main gap
(iScience 29(7):116421, 2026). A satellite sees the top metre on a clear day. This model gives the
water under the advisory on every day: the plankton that feed fish, and the oxygen that decides how
deep fish can go. Both were refused in ADR 0010 because nothing gridded shared this timeline. That
changed: see the 2026-09-15 amendment there.

**The product.** `GLOBAL_ANALYSISFORECAST_BGC_001_028`, daily, 0.25 degree, 50 depths, from
2021-11-01 (read on 2026-09-15: axis 2021-11-01 to 2026-09-24). Two datasets, because Copernicus
split the variables: `chl` sits in the phytoplankton set and `o2` in the biology set. Same free
account as the currents; nothing at demo time.

**It is a model, and it is checked.** A July 2026 feasibility check against every good BGC-Argo
cast in the box found oxygen close at the surface and at depth but too high at 100-150 m, and the
model's chlorophyll about twice the floats' in the top 100 m (research note, 2026-09-15). The bake
collocates both against the floats, so those gaps are published by the bias map rather than
remembered in a document.

**Landing it on the platform's grid** uses the currents adapter's rule: the value at the nearest
source node to each model node, never an average. The argument is the same one ADR 0013 makes for
a jet: a chlorophyll front or an oxygen edge narrower than a cell would be smeared into a value
that exists nowhere, and a float is compared against a point, not a box.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

import numpy as np

from ..grid import Grid
from .base import BoundingBox, FieldSpec
from .copernicus import _HALO_DEGREES, land_on_axes

#: Which Copernicus dataset carries each variable, and what the platform calls it.
DATASETS = {
    "chlorophyll": ("cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m", "chl"),
    "oxygen": ("cmems_mod_glo_bgc-bio_anfc_0.25deg_P1D-m", "o2"),
}

ATTRIBUTION = (
    "E.U. Copernicus Marine Service Information - Global Ocean Biogeochemistry Analysis and "
    "Forecast (GLOBAL_ANALYSISFORECAST_BGC_001_028), chlorophyll and dissolved oxygen at 0.25 "
    "degree. Read with a free Copernicus Marine account at bake time; no account is needed to "
    "view or use this platform."
)

_FIELDS = (
    FieldSpec(
        key="chlorophyll",
        label="Chlorophyll",
        units="mg/m³",
        palette="algae",
        display_min=0.0,
        display_max=1.0,
        group="biology",
        description=(
            "How much plant life is in the water: the plankton at the bottom of the food chain. "
            "Copernicus Marine's biogeochemical model, not a satellite, so it has a value below "
            "the surface and under cloud. Checked against the Argo floats that carry a "
            "fluorometer."
        ),
    ),
    FieldSpec(
        key="oxygen",
        label="Dissolved Oxygen",
        units="mmol/m³",
        palette="oxy",
        display_min=0.0,
        display_max=250.0,
        group="biology",
        description=(
            "How much oxygen is dissolved in the water. Fish need it, so where it runs out is "
            "where they cannot go: the Arabian Sea has one of the largest low-oxygen layers in "
            "the world ocean. Copernicus Marine's biogeochemical model, checked against the Argo "
            "floats that carry an oxygen sensor."
        ),
    ),
)


class CopernicusBgcSource:
    """Reads `chl` and `o2` from Copernicus Marine. Needs stored credentials at bake time."""

    name = "Copernicus Marine (biogeochemistry)"
    attribution = ATTRIBUTION
    endpoint = "data.marine.copernicus.eu/GLOBAL_ANALYSISFORECAST_BGC_001_028"

    def fields(self) -> Sequence[FieldSpec]:
        return _FIELDS

    def timesteps(self) -> Sequence[datetime]:
        # Daily from 2021-11-01. The bake asks for the analysis dates it already has, so this
        # adapter never decides a timeline of its own.
        return ()

    def fetch_grid(self, field_key: str, timestep: datetime, bbox: BoundingBox) -> Grid:
        """A declared Field on Copernicus's own axes, for one day."""
        dataset_id, variable = _dataset_for(field_key)
        subset = _open(dataset_id, variable, bbox, timestep)
        return Grid(
            levels=subset["depth"].values.astype(float),
            latitudes=subset["latitude"].values.astype(float),
            longitudes=subset["longitude"].values.astype(float),
            values=subset[variable].values.astype(float),
        )

    def fetch_on_axes(
        self,
        field_key: str,
        timestep: datetime,
        bbox: BoundingBox,
        levels: np.ndarray,
        latitudes: np.ndarray,
        longitudes: np.ndarray,
    ) -> Grid:
        """One Field on the model's own axes, nearest node in all three dimensions."""
        dataset_id, variable = _dataset_for(field_key)
        return land_on_axes(_open(dataset_id, variable, bbox, timestep), variable, levels, latitudes, longitudes)


def _dataset_for(field_key: str) -> tuple[str, str]:
    if field_key not in DATASETS:
        raise KeyError(
            f"{field_key!r} is not served by {CopernicusBgcSource.name}; it serves "
            f"{', '.join(DATASETS)}"
        )
    return DATASETS[field_key]


def _open(dataset_id: str, variable: str, bbox: BoundingBox, timestep: datetime):
    """One day of one variable over the region. Imported late for the reason `copernicus.py` gives."""
    import copernicusmarine as cm

    day = timestep.strftime("%Y-%m-%d")
    dataset = cm.open_dataset(
        dataset_id=dataset_id,
        minimum_longitude=bbox.west - _HALO_DEGREES,
        maximum_longitude=bbox.east + _HALO_DEGREES,
        minimum_latitude=bbox.south - _HALO_DEGREES,
        maximum_latitude=bbox.north + _HALO_DEGREES,
        start_datetime=day,
        end_datetime=day,
        variables=[variable],
    )
    return dataset.isel(time=0)
