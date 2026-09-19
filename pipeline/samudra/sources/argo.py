"""Source Adapters for Argo Profiles.

Two providers serve the same international programme, and they do not agree on how.

Ifremer's Coriolis GDAC mirror uses lower-case column names and populates the delayed-mode
`*_adjusted` fields. INCOIS's own archive uses upper-case names and ships those adjusted
columns entirely empty, filling the raw ones instead. An adapter that preferred adjusted
blindly would read INCOIS as a table of nothing.

So the column layout is data, not code: a `ProfileColumns` says what a provider calls each
quantity and in what order to prefer its variants, and one parser serves both. That is the
extensibility claim made concrete - a third provider is a new `ProfileColumns` and a small
class, and nothing downstream of `Profile` changes.

Two responsibilities beyond fetching:

Pressure is not depth. Argo reports pressure in decibars. In the upper ocean the two are
numerically close enough that people are casual about it, but they are not the same quantity,
and the platform's whole premise is putting an observation at the right depth inside a model.
So we convert properly rather than pretending 1 dbar == 1 m.

Floats go wrong, and quality control runs in two layers.

Argo's own flags come first. Every value is fetched with the `_qc` column beside it, and a
measurement the programme has already condemned - flag 3, 4 or 9 - is refused. This is checked
per variant, so a delayed-mode value that was flagged bad falls through to the raw one rather
than taking the level with it.

A regional plausible-range check comes second, for what the global standard lets through: this
region has had a float reporting ~20 PSU at the surface, fresher than the Baltic and impossible
in the open Bay of Bengal. Both layers work per channel, so a cast with a failed salinity sensor
still contributes its perfectly good temperature.
"""

from __future__ import annotations

import csv
import io
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Iterable, Sequence, TypeVar

import numpy as np
import requests

from ..density import oxygen_per_volume
from ..tls import ca_bundle
from .base import BoundingBox, Profile

_TIMEOUT = 180

# The second layer, after Argo's own flags. Temperature uses Argo's global gross range check
# (QC Manual, test 4).
#
# Salinity does NOT. Argo's global floor is 2 PSU, which is meant to pass brackish marginal
# seas, and the failed float in this region reports ~20 PSU - comfortably inside it. So this
# floor is a deliberately regional one, stricter than the Argo standard, and it is a judgement
# call rather than a published threshold.
#
# 25 PSU is the floor rather than something tighter because the northern Bay of Bengal really
# is that fresh: the Ganges-Brahmaputra discharge drives monsoon surface salinity down to
# roughly 28 PSU, and clamping at, say, 33 would delete one of the most scientifically
# interesting features in India's own EEZ as though it were instrument error.
#
# Chlorophyll has no Argo gross-range test at all, so both ends of its range are ours. A
# fluorometer that has failed high reports tens of mg/m3; open Indian Ocean water runs about
# 0.05 in the oligotrophic gyre and reaches 2-3 in a coastal bloom, so 20 is generous by an
# order of magnitude and still catches a dead sensor. Negative values are routine and physical
# in raw BGC data - the factory dark count is subtracted, so clean deep water goes slightly
# below zero - and are kept rather than clipped, because clipping them to zero would fabricate
# a floor that the delayed-mode adjustment is there to remove properly.
_PLAUSIBLE = {
    "temperature": (-2.5, 40.0),
    "salinity": (25.0, 41.0),
    "chlorophyll": (-1.0, 20.0),
    # Argo's own gross range for dissolved oxygen, in the micromoles per kilogram floats report
    # (BGC-Argo QC manual, DOXY global range test). Applied before the conversion below.
    "oxygen": (0.0, 600.0),
}

# A cast with fewer points than this is not worth drawing as a Profile.
_MIN_POINTS = 5


# Argo's quality flags, from the QC Manual. 1 is good, 2 probably good, 5 a value the
# delayed-mode operator changed, 8 interpolated - all usable. These three are not: 3 is probably
# bad, 4 is bad, 9 is missing. A measurement the Argo programme has already condemned must not
# arrive here looking like a good one.
_REJECTED_QC = frozenset({"3", "4", "9"})


@dataclass(frozen=True)
class ProfileColumns:
    """What one provider calls each quantity, and which variant to trust first."""

    platform: str
    time: str
    latitude: str
    longitude: str
    pressure: tuple[str, ...]
    temperature: tuple[str, ...]
    salinity: tuple[str, ...]
    # Empty for a provider that does not serve it, which is most of them. A BGC float does, and
    # adding the channel here is the whole cost of reading one - the parser below loops over
    # `measurements` rather than naming three quantities.
    chlorophyll: tuple[str, ...] = ()
    # Dissolved oxygen, in micromoles per kilogram as floats report it. Converted to the model's
    # millimoles per cubic metre in `parse_profiles`, from the cast's own in-situ density.
    oxygen: tuple[str, ...] = ()
    # How this provider spells the quality flag beside a value: `temp_adjusted` + `_qc`. None
    # says the provider serves no flags, which is a fact about the provider rather than a
    # licence to ignore them.
    qc_suffix: str | None = "_qc"
    # The flags on the cast's own fix: where and when it was. A perfect thermometer at a
    # condemned position is a measurement of somewhere else, so a cast flagged 3, 4 or 9 on
    # either is refused whole. None where the provider serves no such column.
    position_qc: str | None = "position_qc"
    time_qc: str | None = "time_qc"

    @property
    def measurements(self) -> tuple[tuple[str, tuple[str, ...]], ...]:
        """Every quantity this layout carries besides pressure, as (name, variants).

        Named quantities rather than a free-form dict, because each one has a plausible range
        and a meaning downstream. A provider that serves none of a quantity simply leaves its
        variants empty and it never appears on a Profile - absence is a fact about the provider,
        not a NaN column.
        """
        return tuple(
            (name, variants)
            for name, variants in (
                ("temperature", self.temperature),
                ("salinity", self.salinity),
                ("chlorophyll", self.chlorophyll),
                ("oxygen", self.oxygen),
            )
            if variants
        )

    def request(self) -> str:
        """Every column this layout can use, as an ERDDAP selector.

        Derived rather than hand-written. It used to be a literal string listing only the
        adjusted columns, so `pressure=("pres_adjusted", "pres")` declared a fallback whose
        second entry was never fetched - the chain had one link and could not fire for the
        provider the demo actually reads.
        """
        names = [self.platform, self.time, self.latitude, self.longitude]
        names += [flag for flag in (self.position_qc, self.time_qc) if flag]
        for variants in (self.pressure, *(v for _, v in self.measurements)):
            for name in variants:
                names.append(name)
                if self.qc_suffix:
                    names.append(f"{name}{self.qc_suffix}")

        seen: set[str] = set()
        return ",".join(n for n in names if not (n in seen or seen.add(n)))


# Ifremer/Coriolis: delayed-mode adjusted values are present and are the better science.
GDAC_COLUMNS = ProfileColumns(
    platform="platform_number",
    time="time",
    latitude="latitude",
    longitude="longitude",
    pressure=("pres_adjusted", "pres"),
    temperature=("temp_adjusted", "temp"),
    salinity=("psal_adjusted", "psal"),
)

# INCOIS: upper case, and the adjusted columns are served empty - raw carries everything.
INCOIS_COLUMNS = ProfileColumns(
    platform="PLATFORM_NUMBER",
    time="time",
    latitude="latitude",
    longitude="longitude",
    pressure=("PRES_ADJUSTED", "PRES"),
    temperature=("TEMP_ADJUSTED", "TEMP"),
    salinity=("PSAL_ADJUSTED", "PSAL"),
    qc_suffix="_QC",
    # INCOIS's archive calls the time flag JULD_QC and serves no position flag at all. Checked
    # against its ERDDAP variable list on 2026-09-15.
    position_qc=None,
    time_qc="JULD_QC",
)


# Ifremer's synthetic BGC product: the same floats, merged onto one pressure axis, carrying the
# biogeochemical channels the core dataset does not. Same host, same tabledap protocol, same
# lower-case adjusted-first convention - so it costs a column layout and four attributes.
#
# Chlorophyll and oxygen are read. Over the twelve-step bake's window this dataset carried usable
# chlorophyll on 49 floats and usable oxygen on none, so oxygen was not declared. Over the
# 36-step window, checked on 2026-09-15, 58 floats carry good-flag chlorophyll and 45 carry
# good-flag oxygen (flag 1 or 8), so oxygen is declared now. Nitrate (27 floats) is not, because
# the platform has no nitrate Field to compare it with.
BGC_COLUMNS = ProfileColumns(
    platform="platform_number",
    time="time",
    latitude="latitude",
    longitude="longitude",
    pressure=("pres_adjusted", "pres"),
    temperature=("temp_adjusted", "temp"),
    salinity=("psal_adjusted", "psal"),
    chlorophyll=("chla_adjusted", "chla"),
    oxygen=("doxy_adjusted", "doxy"),
)


class ArgoErddapSource:
    """In-situ Profiles from the Argo Global Data Assembly Centre (Coriolis/Ifremer)."""

    name = "Argo GDAC (Coriolis/Ifremer ERDDAP)"
    attribution = (
        "Argo float data collected and made freely available by the International Argo "
        "Program and the national programmes that contribute to it (https://argo.ucsd.edu). "
        "The Argo Program is part of the Global Ocean Observing System."
    )
    columns = GDAC_COLUMNS
    endpoint = "https://erddap.ifremer.fr/erddap/tabledap/ArgoFloats.csv"
    # Seconds to wait before each retry. About twenty minutes in all, because the one outage seen
    # (2026-09-15) answered 404 from 11:10 to at least 11:33 IST and was back later that day.
    retry_delays: tuple[float, ...] = (30.0, 120.0, 300.0, 600.0)

    @property
    def requested(self) -> str:
        return self.columns.request()

    def certificates(self) -> str | bool:
        return True

    def fetch_profiles(
        self, bbox: BoundingBox, start: datetime, end: datetime
    ) -> Sequence[Profile]:
        selector = (
            f"{self.requested}"
            f"&time>={start.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            f"&time<={end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            f"&latitude>={bbox.south}&latitude<={bbox.north}"
            f"&longitude>={bbox.west}&longitude<={bbox.east}"
        )
        # Streamed, and parsed line by line as it arrives.
        #
        # `response.text` decodes the whole body into a str while `requests` is still holding the
        # bytes, so the peak is twice the download before a single Profile exists. At twelve
        # Timesteps that was 2 x 175 MB and nobody noticed; at thirty-six it is 2 x 498 MB, and
        # the bake was killed for memory twice at exactly this call - measured, a step from
        # 958 MB to over 3.6 GB inside one 15-second sample.
        def fetch() -> list[Profile]:
            with requests.get(
                f"{self.endpoint}?{selector}",
                timeout=_TIMEOUT,
                verify=self.certificates(),
                stream=True,
            ) as response:
                response.raise_for_status()
                # ERDDAP does not always name the charset, and without one `iter_lines` would
                # hand back bytes rather than the str `csv.reader` needs.
                if not response.encoding:
                    response.encoding = "utf-8"
                return parse_profiles(response.iter_lines(decode_unicode=True), self.columns)

        return with_retries(fetch, delays=self.retry_delays)


class BgcArgoSource(ArgoErddapSource):
    """Chlorophyll and oxygen, from the Argo floats that carry a fluorometer or an optode.

    PS 26067 asks for chlorophyll in the same clause as Argo and glider profiles, and this is
    where it actually exists on a timeline the demo can share. INCOIS publish ocean colour
    themselves - `IRS_chlorophyll_datasets` and `incois_oceansat2_datasets` - but those series
    end 2006-03-21 and 2020-05-01, so neither can sit beside a 2026 analysis.

    INCOIS's own ocean-colour series end in 2006 and 2020. Copernicus's biogeochemical model
    covers this window (`sources/copernicus_bgc.py`), so these floats are what that model is
    checked against: chlorophyll and oxygen join the bias map.
    """

    name = "Argo BGC (Coriolis/Ifremer ERDDAP)"
    attribution = (
        "Argo float data collected and made freely available by the International Argo "
        "Program and the national programmes that contribute to it (https://argo.ucsd.edu). "
        "The Argo Program is part of the Global Ocean Observing System. Biogeochemical "
        "channels from the synthetic BGC product."
    )
    columns = BGC_COLUMNS
    endpoint = "https://erddap.ifremer.fr/erddap/tabledap/ArgoFloats-synthetic-BGC.csv"


class IncoisArgoSource(ArgoErddapSource):
    """The same Profiles, from INCOIS's own archive.

    Present to demonstrate that the adapter seam is real rather than asserted: this provider
    names every column differently and inverts which variant carries the data, and absorbing
    both differences costs a subclass with four attributes and no new parsing code.

    It is deliberately NOT the demo's observation source. INCOIS's Argo archive ends
    2025-04-23 while their gridded analysis runs to 2026-07-30, and collocating a July 2026
    analysis against observations more than a year older would be comparing two different
    oceans. The Ifremer GDAC mirror is current, so that is what the demo uses.
    """

    name = "INCOIS Argo archive"
    attribution = (
        "Indian National Centre for Ocean Information Services (INCOIS), Ministry of Earth "
        "Sciences - INDIAN ARGO Floats Data. Historical archive; coverage ends 2025-04-23."
    )
    columns = INCOIS_COLUMNS
    endpoint = "https://erddap.incois.gov.in/erddap/tabledap/Indian_ARGO_Floats.csv"
    coverage_ends = datetime(2025, 4, 23, tzinfo=timezone.utc)

    def certificates(self) -> str | bool:
        return ca_bundle()  # INCOIS omits an intermediate certificate; see tls.py


T = TypeVar("T")

# Status codes that mean "the server blinked", not "the request is wrong". 404 is here on purpose:
# ERDDAP answers 404 "Currently unknown datasetID" while it reloads a dataset.
_TRANSIENT_STATUS = frozenset({404, 408, 429, 500, 502, 503, 504})


def with_retries(
    fetch: Callable[[], T],
    delays: Sequence[float],
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Run `fetch`, and run it again after each delay while the server is down.

    Retried: a connection error, a timeout, a stream cut mid-download, and the status codes in
    `_TRANSIENT_STATUS`. Not retried: anything else, because a malformed request stays malformed.
    The last error is raised unchanged, so a bake that gives up says what it gave up on.

    The alternative was a second route to the same floats through the GDAC FTP index, one NetCDF
    file per cast. That is a second parser for an outage that lasted under a day, so it is not
    built.
    """
    for attempt in range(len(delays) + 1):
        try:
            return fetch()
        except requests.HTTPError as error:
            status = error.response.status_code if error.response is not None else None
            body = error.response.text if error.response is not None else ""
            # ERDDAP's 404 also means "your query matched nothing", which is an answer.
            if status not in _TRANSIENT_STATUS or "no matching results" in body or attempt == len(delays):
                raise
            reason = f"HTTP {status}"
        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError) as error:
            if attempt == len(delays):
                raise
            reason = type(error).__name__
        print(f"[argo] {reason}; retrying in {delays[attempt]:.0f} s ({attempt + 1} of {len(delays)})")
        sleep(delays[attempt])
    raise AssertionError("unreachable")


def parse_profiles(
    csv_text: str | Iterable[str], columns: ProfileColumns = GDAC_COLUMNS
) -> list[Profile]:
    """Turn one provider's flat CSV into Profiles.

    ERDDAP returns one row per measurement, with the cast identified only by the repetition of
    platform number and time - there is no profile id column. Grouping on that pair is what
    reconstitutes the casts.

    Takes a whole string or an iterable of lines. `csv.reader` never needed the string: it reads
    line by line either way, and accepting the iterable is what lets `fetch_profiles` avoid
    holding the download twice. Measured against the live endpoint, the 36-Timestep window asks
    for 498.4 MB of CSV against 175.0 MB at twelve.
    """
    reader = csv.reader(io.StringIO(csv_text) if isinstance(csv_text, str) else csv_text)
    header = next(reader, None)
    if header is None:
        return []
    next(reader, None)  # ERDDAP's units row

    index = {name: position for position, name in enumerate(header)}
    try:
        platform_at = index[columns.platform]
        time_at = index[columns.time]
        latitude_at = index[columns.latitude]
        longitude_at = index[columns.longitude]
    except KeyError:
        return []  # not a layout this adapter understands

    # Only the variants this provider actually served, in the order we trust them, each paired
    # with its quality flag where one was served.
    pressure_at = _variants(index, columns.pressure, columns.qc_suffix)
    if not pressure_at:
        return []

    # Every other quantity this layout carries, in the order it declares them. A loop rather
    # than three named locals, so a provider that serves a fourth channel - a fluorometer, an
    # oxygen optode - costs a line in `ProfileColumns` and nothing here.
    served = [
        (name, _variants(index, variants, columns.qc_suffix))
        for name, variants in columns.measurements
    ]
    served = [(name, at) for name, at in served if at]

    # The fix flags, where this provider served them. Absent is not condemned.
    fix_flags_at = [
        index[flag] for flag in (columns.position_qc, columns.time_qc) if flag and flag in index
    ]
    refused: set[tuple[str, str]] = set()

    casts: dict[tuple[str, str], list[tuple[float, ...]]] = defaultdict(list)
    positions: dict[tuple[str, str], tuple[float, float]] = {}

    for row in reader:
        try:
            key = (row[platform_at], row[time_at])
            if any(row[at].strip() in _REJECTED_QC for at in fix_flags_at):
                refused.add(key)
                continue
            latitude = float(row[latitude_at])
            longitude = float(row[longitude_at])
            measurement = (
                _first_usable(row, pressure_at),
                *(_first_usable(row, at) for _, at in served),
            )
        except (IndexError, ValueError):
            continue  # a malformed row is not a reason to lose the whole download

        # Everything is parsed before anything is stored. Touching `casts[key]` first would
        # have a defaultdict create the entry, and a row that then failed to parse would leave
        # an empty cast behind - which `zip(*rows)` below cannot unpack, taking down the entire
        # download over one truncated line.
        positions[key] = (latitude, longitude)
        casts[key].append(measurement)

    profiles: list[Profile] = []
    for (platform_id, stamp), rows in casts.items():
        # One condemned fix row condemns the cast: every row of a cast repeats the same fix, so a
        # disagreement between rows is itself a reason not to trust where it was.
        if (platform_id, stamp) in refused:
            continue
        columns_out = [np.array(c, dtype=float) for c in zip(*rows)]
        pressure, channels = columns_out[0], columns_out[1:]

        latitude, longitude = positions[(platform_id, stamp)]
        depths = pressure_to_depth(pressure, latitude)

        values = {
            name: _reject_implausible(channel, name)
            for (name, _), channel in zip(served, channels)
        }
        if "oxygen" in values:
            values["oxygen"] = oxygen_per_volume(
                latitude,
                longitude,
                depths,
                values.get("temperature", np.full(len(depths), np.nan)),
                values.get("salinity", np.full(len(depths), np.nan)),
                values["oxygen"],
            )

        # A level is usable when it has a depth and at least one quantity that survived QC.
        # Chlorophyll counts here like anything else: a BGC cast whose fluorometer worked and
        # whose thermistor did not is still a measurement of this water.
        any_value = np.zeros(len(depths), dtype=bool)
        for channel in values.values():
            any_value |= np.isfinite(channel)
        usable = np.isfinite(depths) & any_value
        if usable.sum() < _MIN_POINTS:
            continue

        order = np.argsort(depths[usable])
        profiles.append(
            Profile(
                platform_id=platform_id,
                latitude=latitude,
                longitude=longitude,
                time=datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),
                depths=depths[usable][order],
                values={name: channel[usable][order] for name, channel in values.items()},
            )
        )

    profiles.sort(key=lambda p: (p.platform_id, p.time))
    return profiles


def _variants(index: dict[str, int], names: tuple[str, ...], qc_suffix: str | None):
    """Column positions for the variants this provider served, each with its flag if there is one."""
    found = []
    for name in names:
        if name not in index:
            continue
        qc = index.get(f"{name}{qc_suffix}") if qc_suffix else None
        found.append((index[name], qc))
    return found


def _first_usable(row: list[str], candidates) -> float:
    """The first variant carrying a number Argo stands behind - adjusted if served, else raw.

    A condemned adjusted value falls through to the raw column rather than taking the level with
    it, which is the whole point of the chain. A raw value that is also condemned does not
    rescue it.
    """
    for position, qc_at in candidates:
        if qc_at is not None and row[qc_at].strip() in _REJECTED_QC:
            continue
        value = _to_float(row[position])
        if np.isfinite(value):
            return value
    return float("nan")


def pressure_to_depth(pressure_dbar, latitude: float):
    """Convert Argo's pressure to depth in metres (Saunders & Fofonoff, as used by UNESCO).

    Gravity varies with latitude, so the same pressure sits at a slightly different depth in
    the Arabian Sea than off Antarctica. Over 2000 m the correction is several metres - small,
    but this is the axis the whole Collocation is aligned on, so it is worth being right.
    """
    pressure = np.asarray(pressure_dbar, dtype=float)
    sin2 = np.sin(np.radians(latitude)) ** 2
    gravity = 9.780318 * (1.0 + 5.2788e-3 * sin2 + 2.36e-5 * sin2**2) + 1.092e-6 * pressure
    numerator = (
        (((-1.82e-15 * pressure + 2.279e-10) * pressure - 2.2512e-5) * pressure + 9.72659)
        * pressure
    )
    return numerator / gravity


def _reject_implausible(values: np.ndarray, quantity: str) -> np.ndarray:
    low, high = _PLAUSIBLE[quantity]
    return np.where((values >= low) & (values <= high), values, np.nan)


def _to_float(raw: str) -> float:
    return float(raw) if raw not in ("", "NaN") else float("nan")
