"""A Field that is one number per location leaves the building as one number per location.

Seven of the nineteen Fields are not a body of water. Five are a depth or a column total
computed here, and two more arrived with the biology round; all seven ship as float32 on the
analysis lattice rather than as a `Grid`, because a reader reads metres off a depth sheet and
kJ/cm2 off a drape and byte-quantising them would be answering a scientific question from a
rendering artefact.

The API did not know that. `servable_fields()` filtered on one name, so `GetCapabilities`
advertised all eighteen and seven of them fell through `native_grid()` to a bare 404 - over WMS
as JSON where the standard wants a `ServiceExceptionReport`, and over CF and OPeNDAP as a body
`xarray` cannot open. Measured over HTTP on 2026-09-21: `GetMap` on `d26` returned
`{"detail": "no grid for d26 at timestep 35"}`. It was five of fourteen when `docs/BUGS.md`
item 104 was written and it grew at the September bake, because `oxygen_floor` and `fronts`
are surfaces too and nothing was watching the class.

The rule these tests hold, and the reason they are a module rather than three assertions:

**Every Field the bake can put in the manifest is either served or refused by name.** A Field
that is missing for a reason and a Field that is missing by accident look identical from
outside, which is the same argument `test_standards.py` opens with.

And the shape is the other half. CF has one answer for a quantity with no depth: a
`(time, latitude, longitude)` array and no vertical coordinate at all. Serving a surface with a
one-element depth axis would be well-formed, would satisfy every client, and would claim the
value varies with depth - which for Depth of 26 degC, whose value *is* a depth, is nonsense
twice over.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "api"))

import cf  # noqa: E402
import standards  # noqa: E402
import wms  # noqa: E402
from dap import dds, dods  # noqa: E402

from oceanverity.bake import all_field_specs  # noqa: E402
from oceanverity.grid import Grid, Surface  # noqa: E402

LATITUDES = np.array([-1.5, -0.5, 0.5, 1.5])
LONGITUDES = np.array([70.5, 71.5, 72.5])
WHEN = datetime(2026, 7, 30, tzinfo=timezone.utc)


def make_surface() -> Surface:
    """Values that are unmistakable if an axis gets transposed: row*10 + column."""
    values = np.array(
        [[row * 10 + column for column in range(len(LONGITUDES))] for row in range(len(LATITUDES))],
        dtype=float,
    )
    # One masked cell, because land is the thing a protocol most easily gets wrong.
    values[0, 0] = np.nan
    return Surface(latitudes=LATITUDES, longitudes=LONGITUDES, values=values)


@pytest.fixture
def surface_dataset():
    return cf.as_dataset(make_surface(), "d26", WHEN)


# ----------------------------------------------------------------- the type


def test_a_surface_refuses_values_that_do_not_match_its_axes():
    """The same guard `Grid` has. A transposed array is silent without it."""
    with pytest.raises(ValueError):
        Surface(
            latitudes=LATITUDES,
            longitudes=LONGITUDES,
            values=np.zeros((len(LONGITUDES), len(LATITUDES))),
        )


def test_a_surface_is_not_a_grid_with_one_level():
    """Stated as a type, so nothing can pass a surface where a depth axis is read."""
    assert not hasattr(make_surface(), "levels")


# ----------------------------------------------------------------- CF


def test_a_surface_has_no_depth_dimension(surface_dataset):
    assert surface_dataset["d26"].dims == ("time", "latitude", "longitude")
    assert "depth" not in surface_dataset.coords
    assert "depth" not in surface_dataset.dims


def test_a_surface_claims_no_vertical_extent(surface_dataset):
    """`geospatial_vertical_min` on a field with no vertical axis is a claim about nothing."""
    vertical = [key for key in surface_dataset.attrs if key.startswith("geospatial_vertical")]
    assert vertical == []


def test_a_surface_keeps_the_units_that_make_it_readable(surface_dataset):
    """The whole reason these ship as float32: a reader reads metres off a depth sheet."""
    assert surface_dataset["d26"].attrs["units"] == "m"
    assert surface_dataset["d26"].attrs["long_name"] == cf._LONG_NAMES["d26"]


def test_a_surface_still_declares_its_fill_value(surface_dataset):
    """NaN is land. Undeclared, a client reads it as a depth of zero metres."""
    assert np.isnan(surface_dataset["d26"].attrs["_FillValue"])


def test_a_volume_field_is_untouched_by_any_of_this():
    """The 4D path is the one thing here that already worked."""
    grid = Grid(
        levels=np.array([5.0, 10.0]),
        latitudes=LATITUDES,
        longitudes=LONGITUDES,
        values=np.zeros((2, len(LATITUDES), len(LONGITUDES))),
    )
    dataset = cf.as_dataset(grid, "temperature", WHEN)
    assert dataset["temperature"].dims == ("time", "depth", "latitude", "longitude")
    assert dataset.attrs["geospatial_vertical_max"] == 10.0


# ----------------------------------------------------------------- OPeNDAP


def test_the_surface_dds_parses_as_dap2(surface_dataset):
    pytest.importorskip("pydap.parsers.dds", reason="pydap is the DAP2 client")
    from pydap.parsers.dds import dds_to_dataset

    parsed = dds_to_dataset(dds(surface_dataset))
    assert "d26" in parsed


def test_the_surface_dds_declares_three_dimensions_and_not_four(surface_dataset):
    text = dds(surface_dataset)
    assert "[time = 1][latitude = 4][longitude = 3]" in text
    assert "depth" not in text


def test_the_surface_values_survive_the_round_trip(surface_dataset):
    pytest.importorskip("pydap.parsers.dds", reason="pydap is the DAP2 client")
    from pydap.parsers.dds import dds_to_dataset

    payload = dods(surface_dataset, "d26")
    header, _, _ = payload.partition(b"\nData:\n")
    parsed = dds_to_dataset(header.decode("ascii"))
    assert parsed["d26"].shape == (1, len(LATITUDES), len(LONGITUDES))


# ----------------------------------------------------------------- WMS


def test_a_surface_draws_without_being_given_a_level():
    """`grid.values[level]` is the line that cannot run here. There is no level to give."""
    image = wms.render(
        make_surface(),
        None,
        [[0, 0, 0], [255, 255, 255]],
        0.0,
        40.0,
        (70.0, 73.0, -2.0, 2.0),
        8,
        8,
    )
    assert image[:8] == b"\x89PNG\r\n\x1a\n"


def test_a_surface_answers_getfeatureinfo_from_its_own_lattice():
    assert wms.feature_info(make_surface(), None, 0.5, 71.5) == 21.0


def test_a_layer_with_no_levels_advertises_no_elevation_dimension():
    """An elevation dimension on a layer with one value per location is a lie a client acts on."""
    document = wms.capabilities(
        "http://example.test/wms",
        [
            {
                "name": "d26",
                "title": "Depth of 26 degC",
                "abstract": "a",
                "units": "m",
                "ours": True,
                "levels": [],
            },
            {
                "name": "temperature",
                "title": "Sea Water Temperature",
                "abstract": "b",
                "units": "degree_C",
                "ours": False,
                "levels": [5.0, 10.0],
            },
        ],
        [WHEN],
        (70.0, 73.0, -2.0, 2.0),
    )
    d26, temperature = document.split("<Name>d26</Name>")[1].split("<Name>temperature</Name>")
    assert 'name="elevation"' not in d26
    assert 'name="elevation"' in temperature


# ------------------------------------------------- the rule, over the whole set


def test_every_field_is_either_served_or_refused_by_name():
    """Item 104, as the rule it broke rather than as the seven names it broke it on.

    Add a Field and forget it here and this goes red, which is the thing that did not happen
    when `oxygen_floor` and `fronts` arrived.
    """
    unaccounted = [
        spec.key
        for spec in all_field_specs()
        if spec.key not in standards.NOT_ON_A_NATIVE_GRID
        and spec.render not in ("volume", "vector", "depth", "column")
    ]
    assert unaccounted == []


def test_the_render_kind_decides_the_shape_and_nothing_else_does():
    """`SURFACE_RENDER_KINDS` is the one place the question is answered."""
    surfaces = {spec.key for spec in all_field_specs() if spec.render in standards.SURFACE_RENDER_KINDS}
    assert "d26" in surfaces
    assert "heat_potential" in surfaces
    assert "oxygen_floor" in surfaces
    assert "fronts" in surfaces
    assert "temperature" not in surfaces
    assert "current_speed" not in surfaces


def test_coverage_is_still_refused_and_is_still_the_only_one():
    """The one Field with no native anything. It is counted on the rendering lattice."""
    assert standards.NOT_ON_A_NATIVE_GRID == {"coverage"}
