"""Source Adapter for the World Ocean Atlas 2023: the 1991-2020 climatological normal.

PS 26067 names **climate monitoring** among the four operational mandates it says a missing 3D
platform impedes. The platform's existing Temperature Anomaly is a departure from the mean of
the baked Timesteps - a seasonal swing, and it says so - so "warmer than usual" did not
yet mean what a forecaster means by it. This is the reference that fixes that.

**Why this fits and dissolved oxygen did not.** ADR 0010 refused oxygen because the only field
for this region was a decadal climatology with no date, and a value with no date cannot share a
ten-day 2026 timeline. That is the right rule for a *value* and the wrong one for a *baseline*:
a climatology having no year is exactly what makes it a climatology. WOA is never drawn as a
value here. It is the thing the 2026 analysis is differenced against.

**Measured, not assumed.** On 2026-09-02 from this machine, both routes answered anonymously:

    thredds-ocean/dodsC/woa23/.../woa23_decav91C0_t07_01.nc.dds   HTTP 200, 2,840 bytes, 1.53 s
    data/oceans/woa/WOA23/.../woa23_decav91C0_t07_01.nc           HTTP 206 on a range request

The OPeNDAP route is the one used, because it is the one that lets a **subset** be asked for.
The global 1-degree monthly field is 180 x 360 x 57; this region is 36 x 56 x 57, about 1.5% of
it, and pulling the whole file for twelve months would be hundreds of megabytes for four.

**The grids line up exactly.** WOA's one-degree nodes are at -89.5, -88.5 ... and 45.5, 46.5 ...
which are the same node centres INCOIS's analysis uses. That is not a happy accident - both
follow the same convention - and it is the entire reason this Field is cheap: no horizontal
regridding, so no chance of quietly differencing two different pieces of water.
`climatology.climatological_anomaly` refuses outright if the axes ever stop matching.

**Three routes to the same numbers, because one of them keeps going down.** NOAA's OPeNDAP server
timed out on 2026-09-14 and answered 503 on 2026-09-15, while the plain HTTPS file server beside it
answered 200 (60.5 MB a month, about 80 s from this machine). So `fetch_grid` reads, in order:

1. a regional subset already saved under `data/woa/` - small, committed like the glider index, so
   a bake normally needs no network for the normal at all;
2. OPeNDAP, which subsets at the server;
3. the whole monthly file over HTTPS, subset here.

Whichever remote route answers, its subset is saved for next time. The atlas files were last
modified 2024-01-29 and a climatology does not change, so a saved copy cannot go stale the way a
saved analysis would.
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Callable

import numpy as np

from ..grid import Grid
from .base import BoundingBox, FieldSpec

#: The 1991-2020 normal, on a one-degree grid, monthly. `decav91C0` is NOAA's own name for that
#: averaging period; `01` in the filename is the grid resolution, not the month.
DECADE = "decav91C0"
RESOLUTION = "1.00"
ROOT = "https://www.ncei.noaa.gov/thredds-ocean/dodsC/woa23/DATA"
HTTPS_ROOT = "https://www.ncei.noaa.gov/data/oceans/woa/WOA23/DATA"

#: Where saved regional subsets live. Server-side, beside `data/glider/`.
CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "woa"

ATTRIBUTION = (
    "World Ocean Atlas 2023, NOAA National Centers for Environmental Information. "
    "Objectively analysed monthly climatological mean for 1991-2020 (decav91C0), one degree. "
    "Read anonymously at bake time (OPeNDAP, or the HTTPS file server when OPeNDAP is down), "
    "with a regional subset kept beside the build; no account is needed at any point."
)

#: The two quantities this platform can difference, and how WOA names them. `t_an` and `s_an`
#: are the *objectively analysed* means - the gridded field - rather than `t_mn`, the statistical
#: mean of the observations in each cell, which is missing wherever nobody sampled.
VARIABLES = {
    "temperature": ("temperature", "t", "t_an"),
    "salinity": ("salinity", "s", "s_an"),
}

#: Anything at or beyond this is WOA's fill value (9.96921e36) rather than a measurement.
#: Read from the variable's own `_FillValue` where the server sends one; this is the floor.
_FILL_THRESHOLD = 1e30

_FIELDS = (
    FieldSpec(
        key="temperature_normal_anomaly",
        label="Temperature vs 1991-2020 Normal",
        units="°C",
        palette="balance",
        display_min=-3.0,
        display_max=3.0,
        description=(
            "How far this analysis sits from the World Ocean Atlas 2023 normal for the same "
            "calendar month, averaged over 1991-2020."
        ),
    ),
)


class WoaClimatologySource:
    """WOA 2023's monthly normal for one region, one variable at a time.

    A `GridSource` in shape but not in timeline: `fetch_grid` takes a **month**, not an instant,
    because a climatology has no year. That is the difference that makes it a baseline rather
    than a value, and the type signature says so.
    """

    name = "World Ocean Atlas 2023 (NOAA NCEI)"
    attribution = ATTRIBUTION
    endpoint = "ncei.noaa.gov/thredds-ocean/dodsC/woa23"
    dataset = f"woa23_{DECADE}"

    def __init__(
        self,
        cache_dir: Path | None = CACHE_DIR,
        open_opendap: Callable[[str], object] | None = None,
        open_https: Callable[[str], object] | None = None,
    ):
        # The two remote routes are injectable so the fallback order is testable offline.
        self.cache_dir = cache_dir
        self._open_opendap = open_opendap or _open
        self._open_https = open_https or _download_and_open
        #: Which route the last `fetch_grid` answered from: "cache", "opendap" or "https".
        self.last_route: str | None = None

    def fields(self) -> list[FieldSpec]:
        return list(_FIELDS)

    def https_url_for(self, variable: str, month: int) -> str:
        """The same file on NOAA's plain HTTPS server, for when OPeNDAP is down."""
        folder, letter, _ = VARIABLES[variable]
        name = f"woa23_{DECADE}_{letter}{month:02d}_01.nc"
        return f"{HTTPS_ROOT}/{folder}/netcdf/{DECADE}/{RESOLUTION}/{name}"

    def url_for(self, variable: str, month: int) -> str:
        """The OPeNDAP address of one month's normal. Public, because it is worth being able to
        paste one into a browser and see the same numbers this read."""
        folder, letter, _ = VARIABLES[variable]
        name = f"woa23_{DECADE}_{letter}{month:02d}_01.nc"
        return f"{ROOT}/{folder}/netcdf/{DECADE}/{RESOLUTION}/{name}"

    def fetch_grid(self, variable: str, month: int, bbox: BoundingBox) -> Grid:
        """The normal for one calendar month over one region, on WOA's own 57 Levels.

        The fill value is turned into NaN here rather than downstream. WOA writes 9.96921e36 for
        "no ocean", and 9.96921e36 degrees Celsius differenced against a real analysis is an
        anomaly of about 1e36, which is finite, enormous and would flatten every colour scale it
        touched.
        """
        if variable not in VARIABLES:
            raise ValueError(f"WOA has no {variable}; it carries {', '.join(VARIABLES)}")
        if not 1 <= month <= 12:
            raise ValueError(f"month must be 1 to 12, got {month}")

        saved = self._from_cache(variable, month, bbox)
        if saved is not None:
            self.last_route = "cache"
            return saved

        errors = []
        for route, opener, url in (
            ("opendap", self._open_opendap, self.url_for(variable, month)),
            ("https", self._open_https, self.https_url_for(variable, month)),
        ):
            try:
                grid = _subset(opener(url), VARIABLES[variable][2], bbox)
            except Exception as error:  # noqa: BLE001 - a route is down in many ways, all the same here
                errors.append(f"{route}: {error}")
                continue
            self.last_route = route
            self._save(variable, month, grid)
            return grid
        raise OSError(
            f"World Ocean Atlas unreachable for {variable} month {month}: " + "; ".join(errors)
        )

    def _cache_path(self, variable: str, month: int) -> Path | None:
        if self.cache_dir is None:
            return None
        letter = VARIABLES[variable][1]
        return Path(self.cache_dir) / f"woa23_{DECADE}_{letter}{month:02d}_region.npz"

    def _save(self, variable: str, month: int, grid: Grid) -> None:
        path = self._cache_path(variable, month)
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            levels=grid.levels,
            latitudes=grid.latitudes,
            longitudes=grid.longitudes,
            values=grid.values.astype(np.float32),
        )

    def _from_cache(self, variable: str, month: int, bbox: BoundingBox) -> Grid | None:
        """The saved subset cut to `bbox`, or None when nothing saved covers it.

        "Covers" means it holds every node a remote read of `bbox` would return. A saved box that
        stops short would hand back a smaller grid with no error, and the anomaly beside it would
        refuse the mismatched axes one step later, far from the cause.
        """
        path = self._cache_path(variable, month)
        if path is None or not path.exists():
            return None
        with np.load(path) as saved:
            lats, lons = saved["latitudes"], saved["longitudes"]
            eps = 1e-6
            rows = (lats >= bbox.south - eps) & (lats <= bbox.north + eps)
            columns = (lons >= bbox.west - eps) & (lons <= bbox.east + eps)
            # One-degree nodes at half degrees: the request holds every node within it.
            wanted_rows = np.arange(np.ceil(bbox.south - 0.5) + 0.5, bbox.north + eps, 1.0)
            wanted_columns = np.arange(np.ceil(bbox.west - 0.5) + 0.5, bbox.east + eps, 1.0)
            if rows.sum() != wanted_rows.size or columns.sum() != wanted_columns.size:
                return None
            return Grid(
                levels=saved["levels"].astype(float),
                latitudes=lats[rows].astype(float),
                longitudes=lons[columns].astype(float),
                values=saved["values"][:, rows][:, :, columns].astype(float),
            )

    def months_for(self, timesteps) -> set[int]:
        """The calendar months a set of Timesteps needs, and no more.

        Three ten-day steps inside one month share one normal, so a bake fetches one file per
        month it touches rather than one per step. A four-month bake fetches four; the 36-step
        bake spans a year and fetches all twelve, which is still a third of one file per step.
        """
        return {when.month for when in timesteps}


def _subset(dataset, name: str, bbox: BoundingBox) -> Grid:
    """One variable over one box, with WOA's fill value turned into Mask."""
    subset = dataset[name].isel(time=0).sel(
        lat=slice(bbox.south, bbox.north), lon=slice(bbox.west, bbox.east)
    )
    values = np.asarray(subset.values, dtype=float)
    fill = dataset[name].attrs.get("_FillValue", dataset[name].attrs.get("missing_value"))
    if fill is not None:
        values = np.where(np.isclose(values, float(fill)), np.nan, values)
    values[np.abs(values) >= _FILL_THRESHOLD] = np.nan
    return Grid(
        levels=np.asarray(dataset["depth"].values, dtype=float),
        latitudes=np.asarray(subset["lat"].values, dtype=float),
        longitudes=np.asarray(subset["lon"].values, dtype=float),
        values=values,
    )


def _download_and_open(url: str):
    """The whole monthly file over HTTPS, read into memory, and the download deleted.

    60.5 MB a month. Used only when OPeNDAP is down and nothing is saved, so at most once per
    month of the atlas on any machine.
    """
    import requests
    import xarray as xr

    handle, path = tempfile.mkstemp(suffix=".nc")
    os.close(handle)
    try:
        with requests.get(url, stream=True, timeout=300) as response:
            response.raise_for_status()
            with open(path, "wb") as out:
                for chunk in response.iter_content(chunk_size=1 << 20):
                    out.write(chunk)
        with xr.open_dataset(path, decode_times=False) as dataset:
            return dataset.load()
    finally:
        os.remove(path)


@lru_cache(maxsize=8)
def _open(url: str):
    """Open one OPeNDAP dataset, once.

    `decode_times=False` on purpose: WOA's time axis is "months since 1955-01-01" with a value
    that is not a real instant, and xarray's decoder either refuses it or invents a date. There
    is no instant to decode - that is what a climatology is - and the month is in the filename.
    """
    import xarray as xr

    return xr.open_dataset(url, engine="pydap", decode_times=False)


def probe(month: int = 7) -> dict:
    """Ask the server what it holds, for the provenance page and for a bake that wants to say
    the source answered. Returns the shape rather than the data."""
    source = WoaClimatologySource()
    dataset = _open(source.url_for("temperature", month))
    return {
        "url": source.url_for("temperature", month),
        "levels": int(dataset["depth"].sizes["depth"]),
        "deepestMetres": float(dataset["depth"].values[-1]),
        "checked": datetime.now(timezone.utc).isoformat(),
    }
