"""Source Adapter for two Copernicus satellite products, read for one thing: surface fronts.

**Temperature:** `SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001`, the Met Office OSTIA analysis, daily,
0.05 degree, gap-free (read 2026-09-15: axis 2024-01-17 to 2026-09-14).

**Chlorophyll:** `OCEANCOLOUR_GLO_BGC_L4_MY_009_104`, the gap-free daily 4 km product (read
2026-09-15: axis 1997-09-04 to 2026-09-07). **Not** the near-real-time twin
`OCEANCOLOUR_GLO_BGC_L4_NRT_009_102`: the research note of 2026-09-15 said that one covered
2023-10-01 onwards, and when read it kept only nineteen days, 2026-08-26 to 2026-09-13. The
multi-year product is the one that shares this bake's window.

Both are **gap-free (L4)**: clouds are filled by the provider's own interpolation. That is the
only way to have a value on every day of a monsoon, and it is also a limit worth saying: a front
drawn under a week of cloud is partly the provider's interpolation, not a clear-sky observation.

What leaves this adapter is not the satellite field. It is the share of each platform cell on a
front, computed by `samudra/fronts.py` - see there for the methods and why it is a share.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

import numpy as np

from ..fronts import chlorophyll_fronts, front_share, onto_grid, thermal_fronts
from .base import BoundingBox, FieldSpec

SST_DATASET = ("METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2", "analysed_sst")
CHL_DATASET = ("cmems_obs-oc_glo_bgc-plankton_my_l4-gapfree-multi-4km_P1D", "CHL")

ATTRIBUTION = (
    "E.U. Copernicus Marine Service Information - Met Office OSTIA sea surface temperature "
    "(SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001) and GlobColour gap-free chlorophyll "
    "(OCEANCOLOUR_GLO_BGC_L4_MY_009_104). Fronts computed by this platform, following the methods "
    "INCOIS name for their fishing advisories; they are not INCOIS advisories."
)

FRONTS_FIELD = FieldSpec(
    key="fronts",
    label="Surface Fronts",
    units="%",
    palette="ice_r",
    display_min=0.0,
    display_max=30.0,
    isosurface=False,
    render="column",
    group="biology",
    description=(
        "Where two bodies of surface water meet: a jump in sea surface temperature or in "
        "chlorophyll. Fronts are the ingredient INCOIS builds its fishing advisories from. This "
        "is not a fishing zone: it is the share of each cell lying on a front, from satellite "
        "fields, by the methods INCOIS name."
    ),
)


class SatelliteFrontsSource:
    """Reads OSTIA temperature and gap-free chlorophyll, and returns fronts on the model's cells."""

    name = "Copernicus Marine (satellite temperature and chlorophyll)"
    attribution = ATTRIBUTION
    endpoint = "data.marine.copernicus.eu/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001 + OCEANCOLOUR_GLO_BGC_L4_MY_009_104"

    def fields(self) -> Sequence[FieldSpec]:
        return (FRONTS_FIELD,)

    def front_share(
        self,
        timestep: datetime,
        bbox: BoundingBox,
        latitudes: np.ndarray,
        longitudes: np.ndarray,
    ) -> tuple[np.ndarray, dict]:
        """Percent of each model cell on a front, and how much of it was thermal and chlorophyll.

        The fronts are found on the satellite grids, joined on the temperature grid, and only then
        counted onto the model's 1 degree cells.
        """
        sst_lats, sst_lons, sst = _read(*SST_DATASET, bbox, timestep)
        chl_lats, chl_lons, chl = _read(*CHL_DATASET, bbox, timestep)
        if np.nanmedian(sst) > 100.0:
            sst = sst - 273.15  # OSTIA publishes kelvin

        thermal = thermal_fronts(sst)
        colour = onto_grid(chlorophyll_fronts(chl), chl_lats, chl_lons, sst_lats, sst_lons)
        ocean = np.isfinite(sst)
        either = (thermal | colour) & ocean

        share = front_share(either, ocean, sst_lats, sst_lons, np.asarray(latitudes), np.asarray(longitudes))
        stats = {
            "thermalPixels": int(thermal.sum()),
            "chlorophyllPixels": int((colour & ocean).sum()),
            "oceanPixels": int(ocean.sum()),
        }
        return share, stats


def _read(dataset_id: str, variable: str, bbox: BoundingBox, timestep: datetime):
    """One day over the region, latitude ascending, as (latitudes, longitudes, float array)."""
    subset = _open(dataset_id, variable, bbox, timestep)
    lats = np.asarray(subset["latitude"].values, dtype=float)
    lons = np.asarray(subset["longitude"].values, dtype=float)
    values = np.asarray(subset[variable].values, dtype=float)
    if lats[0] > lats[-1]:
        lats, values = lats[::-1], values[::-1, :]
    if lons[0] > lons[-1]:
        lons, values = lons[::-1], values[:, ::-1]
    return lats, lons, values


def _open(dataset_id: str, variable: str, bbox: BoundingBox, timestep: datetime):
    """One day of one variable. Imported late for the reason `copernicus.py` gives."""
    import copernicusmarine as cm

    day = timestep.strftime("%Y-%m-%d")
    dataset = cm.open_dataset(
        dataset_id=dataset_id,
        minimum_longitude=bbox.west,
        maximum_longitude=bbox.east,
        minimum_latitude=bbox.south,
        maximum_latitude=bbox.north,
        start_datetime=day,
        end_datetime=day,
        variables=[variable],
    )
    return dataset.isel(time=0).transpose("latitude", "longitude")
