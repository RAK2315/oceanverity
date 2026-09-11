"""A Grid, described the way the rest of oceanography expects to be handed one.

PS 26067 asks for CF Conventions. INCOIS publish CF-1.6 and `sources/incois.py` reads those
conventions directly, which is their compliance rather than ours - everything this platform
writes is a packed binary Volume plus JSON, which is right for a GPU and useless to a scientist.

This module is the other half: one place that turns a `Grid` into a self-describing dataset with
real standard names, so `/api/netcdf`, the OPeNDAP endpoint and the WMS all describe the same
thing in the same words. A consumer never has to be told what is in the file.

Two rules govern everything here.

**It reads the native Grid, never the Volume.** The Volume is quantised to 255 levels,
depth-warped and back-filled across land for the GPU's benefit. Serving that over a scientific
protocol would be the worst possible violation of this project's first rule, because unlike a
picture on screen the consumer cannot see what they have been given.

**A quantity we invented does not get to borrow a standard name.** Temperature, salinity,
density and current speed have real CF standard names. Observation Coverage does not - it is a
count of Argo casts in a neighbourhood, which no vocabulary has a term for - so it is served
with a `long_name` and no `standard_name` at all. Inventing one that looks official is the same
class of error as printing "the conventional oceanographic scale for observation coverage".

**Every Field is in these tables, and a test says so.** They covered five of the fifteen for a
round, and `.get(field, "1")` served the other ten as dimensionless with their internal key as
their name - `incois_rmse`, an error estimate in degrees Celsius, handed to a client as a bare
number over the endpoints this docstring says exist so nobody has to be told what is in the
file. A missing entry now fails `tests/test_standards.py` rather than falling back to a
plausible-looking default.
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
import xarray as xr

CONVENTIONS = "CF-1.8"

# Standard names from the CF standard name table. A Field missing from here is served with a
# long_name only, which is what CF asks you to do when no standard name applies.
_STANDARD_NAMES = {
    "temperature": "sea_water_temperature",
    "salinity": "sea_water_practical_salinity",
    "density": "sea_water_sigma_theta",
    "current_speed": "sea_water_speed",
    # A departure from the mean of this bake's own steps is not an anomaly in the CF sense,
    # which means a departure from a climatology. There is no standard name for what this is.
    "temperature_anomaly": None,
    "coverage": None,
    # The other nine are deliberately nameless, each for its own reason, and none of them is
    # "we could not be bothered to look":
    #
    # `temperature_normal_anomaly` *is* a climatological anomaly, but CF expresses an anomaly
    # through a reference period this table cannot state, and a name asserting the wrong period
    # is worse than none. `incois_casts`, `incois_rmse` and `analysis_spread` are evidence about
    # an analysis rather than properties of sea water, which is what the standard name table
    # describes. The five hazard Fields are threshold crossings computed to this platform's own
    # criterion - `hazard.py` states each one - and CF's mixed-layer names carry a qualifier
    # saying which criterion produced them, so borrowing one would assert a definition we have
    # not checked ours against.
    "temperature_normal_anomaly": None,
    "incois_casts": None,
    "incois_rmse": None,
    "analysis_spread": None,
    "heat_potential": None,
    "d26": None,
    "mixed_layer_depth": None,
    "isothermal_layer_depth": None,
    "barrier_layer": None,
}

# Short, label-like, the way CF means a long name: one noun phrase a client can put on an axis
# or in a layer list. Anything longer belongs in `comment` below, which is what CF has it for -
# and what keeps the dataset `title` from becoming a paragraph.
_LONG_NAMES = {
    "temperature": "Sea water temperature",
    "salinity": "Sea water practical salinity",
    "density": "Sea water potential density anomaly (sigma-theta)",
    "temperature_anomaly": "Sea water temperature departure from this build's analysis mean",
    "coverage": "Count of Argo profile casts through this depth",
    "temperature_normal_anomaly": (
        "Sea water temperature departure from the 1991-2020 monthly normal"
    ),
    "incois_casts": "Argo observations used by INCOIS's Kessler-McCreary analysis",
    "incois_rmse": (
        "Root-mean-square error published by INCOIS for the Kessler-McCreary analysis"
    ),
    "analysis_spread": "Difference between INCOIS's two analyses of the same Argo profiles",
    "current_speed": "Magnitude of the horizontal sea water velocity",
    "heat_potential": "Tropical cyclone heat potential",
    "d26": "Depth of the 26 degree Celsius isotherm",
    "mixed_layer_depth": "Depth of the density-defined mixed layer",
    "isothermal_layer_depth": "Depth of the temperature-defined isothermal layer",
    "barrier_layer": "Barrier layer thickness",
}

# What the long name cannot say in a noun phrase, on the variable itself.
#
# No count and no dates in any of these: this is a module constant and cannot see the bake
# window, so a figure here goes stale the first time `--timesteps` moves and nothing can notice.
# The steps themselves are on the time axis of every dataset this serves.
_COMMENTS = {
    "temperature_anomaly": (
        "Departure from the mean of the analysis steps in this build. Not a climatological "
        "anomaly, which is why it carries no standard name."
    ),
    "coverage": (
        "Argo profile casts within 334 km whose dive passed through this depth, in the ten days "
        "around this analysis step. Evidence for the analysis, not a model field."
    ),
    "temperature_normal_anomaly": (
        "Differenced against the World Ocean Atlas 2023 objectively analysed mean for the same "
        "calendar month over 1991-2020. Undefined below 1500 m, where the atlas has no normal."
    ),
    "incois_casts": "The provider's own evidence, restated on its native grid.",
    "incois_rmse": "The provider's own error estimate, restated on its native grid.",
    "analysis_spread": (
        "Variational minus Kessler-McCreary, subtracted here. An uncertainty signal, not a "
        "measurement."
    ),
    "current_speed": (
        "Computed from E.U. Copernicus Marine's horizontal current velocity analysis at 1/12 "
        "degree, landed on this grid by nearest node."
    ),
    "heat_potential": (
        "Heat stored above 26 degrees Celsius, integrated from the sea surface down to the "
        "depth of the 26 degree isotherm."
    ),
    "mixed_layer_depth": (
        "By this platform's own sigma-theta criterion; see samudra/hazard.py for the threshold "
        "and for the vertical-resolution limit every crossing inherits."
    ),
    "isothermal_layer_depth": (
        "By this platform's own temperature criterion; see samudra/hazard.py for the threshold "
        "and for the vertical-resolution limit every crossing inherits."
    ),
    "barrier_layer": (
        "Isothermal layer depth minus mixed layer depth. Negative where salinity stratifies "
        "water the temperature says is mixed."
    ),
}

# UDUNITS strings, which are not the display units in the manifest: practical salinity is
# dimensionless in CF and PSU is not a UDUNITS term, and a count of casts is "1" however the
# colourbar labels it. The long_name carries what is being counted.
_UNITS = {
    "temperature": "degree_Celsius",
    "salinity": "1",  # practical salinity is dimensionless in CF; PSU is not a CF unit
    "density": "kg m-3",
    "temperature_anomaly": "degree_Celsius",
    "coverage": "1",
    "temperature_normal_anomaly": "degree_Celsius",
    "incois_casts": "1",
    "incois_rmse": "degree_Celsius",
    "analysis_spread": "degree_Celsius",
    "current_speed": "m s-1",
    "heat_potential": "kJ cm-2",
    "d26": "m",
    "mixed_layer_depth": "m",
    "isothermal_layer_depth": "m",
    "barrier_layer": "m",
}

# Who published the numbers, as the CF global attributes a consumer reads first.
#
# These were hardcoded to INCOIS's Variational analysis for every Field, so a NetCDF file of
# current speed - which is Copernicus Marine's velocity analysis - went out attributed to
# INCOIS, with INCOIS's dataset page as its `references`. The default below is the honest one
# for anything computed from their temperature and salinity; the entries are the Fields for
# which it is not.
_DEFAULT_SOURCE = {
    "institution": "Indian National Centre for Ocean Information Services (INCOIS)",
    "source": (
        "INCOIS ARGO 10-day gridded analysis (Variational Analysis Methodology), "
        "dataset incois_argo_10d_VAM, served on its native axes"
    ),
    "references": "https://erddap.incois.gov.in/erddap/griddap/incois_argo_10d_VAM.html",
}

_SOURCES = {
    "incois_casts": {
        "institution": "Indian National Centre for Ocean Information Services (INCOIS)",
        "source": (
            "INCOIS ARGO 10-day gridded analysis (Kessler-McCreary), dataset "
            "incois_argo_10day_McCreary, served on its native axes"
        ),
        "references": (
            "https://erddap.incois.gov.in/erddap/griddap/incois_argo_10day_McCreary.html"
        ),
    },
    "current_speed": {
        "institution": "E.U. Copernicus Marine Service",
        "source": (
            "Speed computed by Samudra 3D from the Global Ocean Physics Analysis and Forecast "
            "(GLOBAL_ANALYSISFORECAST_PHY_001_024) horizontal current velocity at 1/12 degree, "
            "landed on the analysis grid by nearest node"
        ),
        "references": "https://doi.org/10.48670/moi-00016",
    },
    "temperature_normal_anomaly": {
        "institution": (
            "Samudra 3D, from INCOIS and NOAA National Centers for Environmental Information"
        ),
        "source": (
            "INCOIS ARGO 10-day gridded analysis (Variational Analysis Methodology) "
            "differenced against World Ocean Atlas 2023 monthly climatological mean for "
            "1991-2020 (decav91C0), one degree"
        ),
        "references": "https://www.ncei.noaa.gov/products/world-ocean-atlas",
    },
    "analysis_spread": {
        "institution": "Samudra 3D, from INCOIS",
        "source": (
            "Difference between INCOIS's two analyses of the same Argo profiles, "
            "incois_argo_10d_VAM minus incois_argo_10day_McCreary"
        ),
        "references": "https://erddap.incois.gov.in/erddap/griddap/index.html",
    },
}
_SOURCES["incois_rmse"] = _SOURCES["incois_casts"]


def as_dataset(grid, field: str, when: datetime, extra_attributes: dict | None = None):
    """One Grid at one Timestep as a CF-1.8 `xarray.Dataset`.

    Axes are named and attributed so a client can orient itself without being told: depth is
    positive down and carries `positive: "down"`, which is the attribute that stops a plotting
    library drawing the ocean upside down.
    """
    depth = xr.DataArray(
        np.asarray(grid.levels, dtype="float32"),
        dims="depth",
        attrs={
            "standard_name": "depth",
            "long_name": "Depth below sea surface",
            "units": "m",
            "positive": "down",
            "axis": "Z",
        },
    )
    latitude = xr.DataArray(
        np.asarray(grid.latitudes, dtype="float32"),
        dims="latitude",
        attrs={
            "standard_name": "latitude",
            "long_name": "Latitude",
            "units": "degrees_north",
            "axis": "Y",
        },
    )
    longitude = xr.DataArray(
        np.asarray(grid.longitudes, dtype="float32"),
        dims="longitude",
        attrs={
            "standard_name": "longitude",
            "long_name": "Longitude",
            "units": "degrees_east",
            "axis": "X",
        },
    )
    time = xr.DataArray(
        np.array([np.datetime64(when.replace(tzinfo=None), "s")]),
        dims="time",
        attrs={"standard_name": "time", "long_name": "Analysis time", "axis": "T"},
    )

    variable = xr.DataArray(
        np.asarray(grid.values, dtype="float32")[np.newaxis, ...],
        dims=("time", "depth", "latitude", "longitude"),
        attrs={
            key: value
            for key, value in {
                "standard_name": _STANDARD_NAMES.get(field),
                "long_name": _LONG_NAMES.get(field, field),
                "units": _UNITS.get(field, "1"),
                "comment": _COMMENTS.get(field),
                # NaN is the mask - land, or sea floor above this level. Declared, so a client
                # does not read it as a value of zero.
                "_FillValue": np.float32(np.nan),
                "missing_value": np.float32(np.nan),
            }.items()
            if value is not None
        },
    )

    dataset = xr.Dataset(
        {field: variable},
        coords={"time": time, "depth": depth, "latitude": latitude, "longitude": longitude},
        attrs={
            "Conventions": CONVENTIONS,
            "title": f"Samudra 3D - {_LONG_NAMES.get(field, field)}",
            **_SOURCES.get(field, _DEFAULT_SOURCE),
            "comment": (
                "Served from the native Grid, never from the rendering Volume: the Volume is "
                "quantised to 255 levels, depth-warped and back-filled across land for the GPU."
            ),
            "geospatial_lat_min": float(np.min(grid.latitudes)),
            "geospatial_lat_max": float(np.max(grid.latitudes)),
            "geospatial_lon_min": float(np.min(grid.longitudes)),
            "geospatial_lon_max": float(np.max(grid.longitudes)),
            "geospatial_vertical_min": float(np.min(grid.levels)),
            "geospatial_vertical_max": float(np.max(grid.levels)),
            "geospatial_vertical_positive": "down",
            "time_coverage_start": when.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "time_coverage_end": when.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )
    if extra_attributes:
        dataset.attrs.update(extra_attributes)
    return dataset


def to_netcdf_bytes(dataset) -> bytes:
    """Serialise to NetCDF in memory. `to_netcdf(None)` returns bytes rather than writing."""
    return dataset.to_netcdf(None)
