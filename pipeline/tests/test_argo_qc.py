"""Argo's own quality flags, and the fallback chain that could not fire without them.

ADR 0008 describes this platform's salinity floor as *stricter* than the Argo standard. That was
true of the gross range check and it quietly implied the rest of Argo's tests were running. They
were not: the request asked for values and never for the `_qc` columns beside them, so a sensor
the Argo programme had already condemned arrived looking exactly like a good one.

The second half is the same mistake seen from the other side. `ProfileColumns` declares
`pressure=("pres_adjusted", "pres")` - prefer the delayed-mode value, fall back to the raw one -
but the request was a hand-written string that only ever asked for the adjusted columns, so the
fallback list had one entry and the "chain" could not fire for the provider the demo reads.
"""

from __future__ import annotations

import numpy as np
import pytest

from oceanverity.sources.argo import (
    GDAC_COLUMNS,
    ArgoErddapSource,
    IncoisArgoSource,
    parse_profiles,
)

HEAD = (
    "platform_number,time,latitude,longitude,"
    "pres_adjusted,pres_adjusted_qc,pres,pres_qc,"
    "temp_adjusted,temp_adjusted_qc,temp,temp_qc,"
    "psal_adjusted,psal_adjusted_qc,psal,psal_qc\n"
    ",UTC,degrees_north,degrees_east,"
    "decibar,,decibar,,degree_Celsius,,degree_Celsius,,PSU,,PSU,\n"
)


def cast(rows: list[str]) -> str:
    return HEAD + "".join(rows)


def row(pressure, temp, temp_qc, psal, psal_qc, *, pres_qc="1", raw_temp="", raw_temp_qc=""):
    return (
        f"1900001,2026-06-09T20:58:41Z,3.87,80.22,"
        f"{pressure},{pres_qc},{pressure},{pres_qc},"
        f"{temp},{temp_qc},{raw_temp},{raw_temp_qc},"
        f"{psal},{psal_qc},,\n"
    )


def only(text):
    profiles = parse_profiles(text, GDAC_COLUMNS)
    assert len(profiles) == 1
    return profiles[0]


# ---------------------------------------------------------------- what gets asked for

def test_the_request_asks_for_every_variant_the_layout_declares():
    """The chain is only a chain if the raw columns are actually fetched."""
    asked = ArgoErddapSource().requested.split(",")
    for variant in (*GDAC_COLUMNS.pressure, *GDAC_COLUMNS.temperature, *GDAC_COLUMNS.salinity):
        assert variant in asked, f"{variant} is declared but never requested"


def test_the_request_asks_for_the_quality_flag_beside_every_value():
    asked = ArgoErddapSource().requested.split(",")
    for variant in (*GDAC_COLUMNS.temperature, *GDAC_COLUMNS.salinity):
        assert f"{variant}_qc" in asked, f"{variant} is requested without its flag"


def test_a_provider_with_upper_case_columns_gets_upper_case_flags():
    asked = IncoisArgoSource().requested.split(",")
    assert "TEMP_ADJUSTED_QC" in asked
    assert "PSAL_QC" in asked
    assert "TEMP_QC" in asked


def test_the_request_never_repeats_a_column():
    asked = ArgoErddapSource().requested.split(",")
    assert len(asked) == len(set(asked))


# ---------------------------------------------------------------- what gets rejected

@pytest.mark.parametrize("flag", ["3", "4", "9"])
def test_a_condemned_measurement_is_dropped(flag):
    """Argo flag 3 is probably bad, 4 is bad, 9 is missing. None of them is data."""
    text = cast([row(5.0 + 10 * i, 29.0, flag, 35.0, "1") for i in range(6)])
    assert np.isnan(only(text).values["temperature"]).all()


@pytest.mark.parametrize("flag", ["1", "2", "5", "8"])
def test_a_flag_that_is_not_a_rejection_is_kept(flag):
    """2 is probably good, 5 is a changed value, 8 is interpolated. All usable."""
    text = cast([row(5.0 + 10 * i, 29.0, flag, 35.0, "1") for i in range(6)])
    assert np.isfinite(only(text).values["temperature"]).all()


def test_a_bad_flag_on_one_channel_leaves_the_other_alone():
    """A failed salinity sensor must not cost the cast its perfectly good temperature - the same
    rule the plausible-range check already follows."""
    text = cast([row(5.0 + 10 * i, 29.0, "1", 35.0, "4") for i in range(6)])
    profile = only(text)
    assert np.isfinite(profile.values["temperature"]).all()
    assert np.isnan(profile.values["salinity"]).all()


def test_a_condemned_adjusted_value_falls_through_to_the_raw_one():
    """The chain firing, at last. Delayed mode flagged the adjusted value bad; the raw column
    beside it is flagged good and carries a number."""
    text = cast(
        [
            row(5.0 + 10 * i, 29.0, "4", 35.0, "1", raw_temp="28.5", raw_temp_qc="1")
            for i in range(6)
        ]
    )
    assert only(text).values["temperature"] == pytest.approx(28.5)


def test_it_does_not_fall_through_to_a_raw_value_that_is_also_condemned():
    text = cast(
        [
            row(5.0 + 10 * i, 29.0, "4", 35.0, "1", raw_temp="28.5", raw_temp_qc="4")
            for i in range(6)
        ]
    )
    assert np.isnan(only(text).values["temperature"]).all()


def test_a_provider_serving_no_flags_at_all_still_parses():
    """Backward compatibility is not optional: a provider that omits the flag columns is not
    thereby serving nothing."""
    plain = (
        "platform_number,time,latitude,longitude,pres_adjusted,temp_adjusted,psal_adjusted\n"
        ",UTC,degrees_north,degrees_east,decibar,degree_Celsius,PSU\n"
    ) + "".join(
        f"1900001,2026-06-09T20:58:41Z,3.87,80.22,{5.0 + 10 * i},29.0,35.0\n" for i in range(6)
    )
    profile = only(plain)
    assert np.isfinite(profile.values["temperature"]).all()


def test_a_flagged_pressure_drops_the_level_entirely():
    """Depth is the axis the whole Collocation is aligned on. A pressure Argo does not stand
    behind is not a level, whatever the thermometer said."""
    rows = [row(5.0 + 10 * i, 29.0, "1", 35.0, "1") for i in range(6)]
    rows.append(row(500.0, 9.0, "1", 35.0, "1", pres_qc="4"))
    profile = only(cast(rows))
    assert len(profile) == 6
    assert profile.depths.max() < 200


# ---------------------------------------------------------------- where and when the cast was

POS_HEAD = (
    "platform_number,time,latitude,longitude,position_qc,time_qc,"
    "pres_adjusted,pres_adjusted_qc,temp_adjusted,temp_adjusted_qc\n"
    ",UTC,degrees_north,degrees_east,,,decibar,,degree_Celsius,\n"
)


def fixed_cast(position_qc: str, time_qc: str, platform: str = "1900001") -> str:
    return "".join(
        f"{platform},2026-06-09T20:58:41Z,3.87,80.22,{position_qc},{time_qc},"
        f"{5.0 + 10 * i},1,29.0,1\n"
        for i in range(6)
    )


def test_the_request_asks_for_the_position_and_time_flags():
    """A good thermometer at a wrong position is a measurement of somewhere else."""
    asked = ArgoErddapSource().requested.split(",")
    assert "position_qc" in asked
    assert "time_qc" in asked


def test_incois_asks_for_its_own_time_flag_and_no_position_flag_it_does_not_serve():
    """INCOIS's archive calls the time flag JULD_QC and serves no position flag at all
    (checked against its ERDDAP variable list on 2026-09-15)."""
    asked = IncoisArgoSource().requested.split(",")
    assert "JULD_QC" in asked
    assert not any("POSITION" in name.upper() for name in asked)


@pytest.mark.parametrize("flag", ["3", "4", "9"])
def test_a_cast_with_a_condemned_position_is_refused(flag):
    text = POS_HEAD + fixed_cast(flag, "1")
    assert parse_profiles(text, GDAC_COLUMNS) == []


@pytest.mark.parametrize("flag", ["3", "4", "9"])
def test_a_cast_with_a_condemned_time_is_refused(flag):
    text = POS_HEAD + fixed_cast("1", flag)
    assert parse_profiles(text, GDAC_COLUMNS) == []


@pytest.mark.parametrize("flag", ["1", "2", "5", "8", ""])
def test_a_usable_or_absent_fix_flag_keeps_the_cast(flag):
    text = POS_HEAD + fixed_cast(flag, flag)
    assert len(parse_profiles(text, GDAC_COLUMNS)) == 1


def test_a_bad_fix_on_one_cast_leaves_the_next_cast_alone():
    text = POS_HEAD + fixed_cast("4", "1", platform="1900001") + fixed_cast("1", "1", platform="1900002")
    assert [p.platform_id for p in parse_profiles(text, GDAC_COLUMNS)] == ["1900002"]


# ---------------------------------------------------------------- a provider that blinks

class _Flaky:
    """Fails `failures` times the way Ifremer did on 2026-09-15, then answers."""

    def __init__(self, failures: int, error: Exception):
        self.failures = failures
        self.error = error
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls <= self.failures:
            raise self.error
        return ["ok"]


def test_a_transient_outage_is_retried_until_it_answers():
    import requests

    from oceanverity.sources.argo import with_retries

    waits: list[float] = []
    flaky = _Flaky(2, requests.ConnectionError("down"))
    assert with_retries(flaky, delays=(1.0, 2.0, 3.0), sleep=waits.append) == ["ok"]
    assert flaky.calls == 3
    assert waits == [1.0, 2.0]


def test_an_unknown_dataset_answer_is_treated_as_an_outage():
    """ERDDAP said 404 "Currently unknown datasetID" for ArgoFloats three times on 15 Sep, and it
    came back later the same day. A 404 from a dataset that exists is a blink, not a verdict."""
    import requests

    from oceanverity.sources.argo import with_retries

    response = requests.Response()
    response.status_code = 404
    flaky = _Flaky(1, requests.HTTPError("404", response=response))
    assert with_retries(flaky, delays=(0.0,), sleep=lambda _: None) == ["ok"]


def test_it_gives_up_after_the_last_wait_and_says_why():
    import requests

    from oceanverity.sources.argo import with_retries

    flaky = _Flaky(10, requests.Timeout("slow"))
    with pytest.raises(requests.Timeout):
        with_retries(flaky, delays=(0.0, 0.0), sleep=lambda _: None)
    assert flaky.calls == 3


def test_a_bad_request_is_not_retried():
    """A 400 is our fault. Waiting twenty minutes to be told the same thing helps nobody."""
    import requests

    from oceanverity.sources.argo import with_retries

    response = requests.Response()
    response.status_code = 400
    flaky = _Flaky(10, requests.HTTPError("400", response=response))
    with pytest.raises(requests.HTTPError):
        with_retries(flaky, delays=(0.0, 0.0), sleep=lambda _: None)
    assert flaky.calls == 1


def test_a_query_that_matched_nothing_is_not_retried():
    """ERDDAP also answers 404 for "Your query produced no matching results". That is an answer,
    not an outage, and waiting twenty minutes to hear it again helps nobody."""
    import requests

    from oceanverity.sources.argo import with_retries

    response = requests.Response()
    response.status_code = 404
    response._content = b'Error {\n    code=404;\n    message="Not Found: Your query produced no matching results. (nRows = 0)";\n}'
    flaky = _Flaky(10, requests.HTTPError("404", response=response))
    with pytest.raises(requests.HTTPError):
        with_retries(flaky, delays=(0.0, 0.0), sleep=lambda _: None)
    assert flaky.calls == 1
