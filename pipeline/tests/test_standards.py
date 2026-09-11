"""Every Field is described before it leaves the building, and the tables that describe it are
checked against the whole set rather than against whichever Field is being edited.

This is the seam where a defect is invisible from inside. A Field on screen is described by
`guide.ts`, a legend, a colourbar and a unit under the cursor; the same Field over CF, OPeNDAP
or WMS is described by two tables in `api/`, read by software with no human in the loop. Both
tables were written when there were five Fields and neither grew with the count:

- `cf.py`'s `_UNITS` and `_LONG_NAMES` covered five of fifteen, and `.get(field, "1")` served
  the other ten as dimensionless with their internal key as their name. `incois_rmse` is an
  error estimate in degrees Celsius and went out as a bare number.
- `standards.py` had a two-element `OURS` set and captioned everything else as "INCOIS's
  published analysis". That attributed E.U. Copernicus Marine's current analysis to INCOIS and
  gave away the five hazard Fields, which INCOIS stopped publishing in 2019.

Neither could be caught by running anything: both defaults produce a well-formed document
saying something false. So the check is completeness against `bake.all_field_specs()`, which is
every Field the bake can put in the manifest, known without fetching anything.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "api"))

import cf  # noqa: E402
import standards  # noqa: E402

from samudra.bake import all_field_specs  # noqa: E402

FIELD_KEYS = [spec.key for spec in all_field_specs()]


def test_every_field_has_cf_units():
    """A Field missing from `_UNITS` is served as dimensionless, which is a claim, not a gap."""
    missing = [key for key in FIELD_KEYS if key not in cf._UNITS]
    assert missing == []


def test_every_field_has_a_cf_long_name():
    """The fallback is the internal key, which is a name only this repository can read."""
    missing = [key for key in FIELD_KEYS if key not in cf._LONG_NAMES]
    assert missing == []


def test_every_field_has_decided_about_a_standard_name():
    """Present-and-None is a decision; absent is an omission. `.get` cannot tell them apart."""
    missing = [key for key in FIELD_KEYS if key not in cf._STANDARD_NAMES]
    assert missing == []


def test_no_field_borrows_a_standard_name_this_platform_invented():
    """The module's own rule. Every name declared here is in the CF standard name table."""
    real = {
        "sea_water_temperature",
        "sea_water_practical_salinity",
        "sea_water_sigma_theta",
        "sea_water_speed",
    }
    declared = {name for name in cf._STANDARD_NAMES.values() if name is not None}
    assert declared <= real


def test_a_degree_celsius_field_is_not_served_as_dimensionless():
    """The `incois_rmse` regression, stated as the rule it broke.

    Any Field the manifest labels in degrees Celsius must carry a temperature unit over CF. The
    manifest's own label is the display one, so this reads the spec rather than the CF table to
    decide which Fields it applies to.
    """
    for spec in all_field_specs():
        if spec.units.startswith("°C"):
            assert cf._UNITS[spec.key] == "degree_Celsius", spec.key


def test_every_field_has_a_provenance_sentence():
    """Including the ones not served: a reader who asks for coverage gets told why, not a 404."""
    missing = [key for key in FIELD_KEYS if key not in standards.PROVENANCE]
    assert missing == []


def test_nothing_computed_here_is_captioned_as_somebody_elses_analysis():
    """The half of item 105 that gave the project's own work away.

    Every Field this platform derived rather than restated - the two anomalies, density, the
    analysis spread, current speed and the five hazard quantities - must say it was computed
    here. `restated` is reserved for a provider's own published numbers on their own grid.
    """
    computed = {
        "density",
        "temperature_anomaly",
        "temperature_normal_anomaly",
        "analysis_spread",
        "current_speed",
        "coverage",
        "heat_potential",
        "d26",
        "mixed_layer_depth",
        "isothermal_layer_depth",
        "barrier_layer",
    }
    for key in computed:
        assert standards.PROVENANCE[key].startswith("Computed"), key
    assert standards.OURS == computed


def test_current_speed_is_not_attributed_to_incois():
    """It is E.U. Copernicus Marine's analysis, over a protocol that hides its own provenance."""
    assert "Copernicus" in standards.PROVENANCE["current_speed"]
    assert "INCOIS" not in cf._SOURCES["current_speed"]["institution"]
    assert "incois" not in cf._SOURCES["current_speed"]["references"]


def test_a_field_with_no_provenance_entry_claims_nothing():
    """The default is what went wrong, so the replacement default asserts nothing about anyone."""
    assert "INCOIS" not in standards.UNATTRIBUTED
    assert "Computed" not in standards.UNATTRIBUTED
