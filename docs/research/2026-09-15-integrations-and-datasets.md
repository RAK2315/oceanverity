# Integrations INCOIS needs, and the datasets the build rests on

Compiled 2026-09-15. Everything below was read or tested from the build machine on that date unless
a line says otherwise. Box = 45-100 E, 10 S-25 N. Window = 10 Aug 2025 to 30 Jul 2026. No project
file was edited. The HTML version of this note carries the figures.

## Summary

- **Recommendation: build the fishing-ground water column.** Show the water under INCOIS's Potential
  Fishing Zone lines - chlorophyll, oxygen, mixed layer and thermocline - with a Copernicus
  biogeochemical model checked against the BGC-Argo floats already in the build. Reason: it
  answers the one operational mandate the PS names that the build still does not, and it goes
  straight at the gaps INCOIS itself published in June 2026 (clouds in the monsoon, advice for
  single species, no way to check the advice).
- **Four more integrations are strong**, and they share one idea with the first: *pick an INCOIS
  advisory, see the water under it, and see the instruments that checked it.* In order: INCOIS's own
  current instruments (HF radar, OMNI moorings with current profilers, drifters) as the score for the
  current field; marine heatwaves traced below the surface; a scorecard for INCOIS's daily ocean
  forecasts; and wind plus wave drift added to the drift model.
- **Three things the build says are wrong now, and two are big.** (1) "India's HF-radar and ADCP
  data are not open": INCOIS's public Ocean Observation Network portal serves HF-radar vectors
  from 1 Jan 2026 and hourly OMNI mooring currents to 100 m with no login. Its data policy still
  restricts EEZ data, so this is a permission question, not a technical one. (2) "No gridded
  chlorophyll or oxygen shares this timeline": Copernicus's biogeochemical model and its gap-free
  satellite chlorophyll both cover the whole window, with the same free account the build already
  uses. (3) `incois.gov.in/thredds` is not an empty server any more.
- **Two dependencies are fragile today.** Ifremer's `ArgoFloats` answered at the first check and then returned
  "Currently unknown datasetID" on three later tries (the last at 11:33 IST). The build has no fallback for it. NOAA's WOA23
  OPeNDAP returned 503 today and timed out yesterday.
- **Still unverified:** whether INCOIS's VAM analysis takes in moored-buoy data. INCOIS's own
  ocean model (INCOIS-GODAS) does assimilate RAMA and NIOT moorings, so any sentence about "data
  INCOIS did not ingest" has to name the VAM analysis.

---

## Update, same evening: second research pass, re-checked

An independent research pass was checked claim by claim from the build machine. Full table and the
fix list with file locations: [`docs/plan/06-fixes-from-2026-09-15-research.md`](../plan/06-fixes-from-2026-09-15-research.md).

- **OMNI moored buoy data is view-only.** INCOIS Data Holdings: "Public Access with only
  visualisation option". **HF radar is "Registered access through Website".** Both need a request;
  the portal data must not be scraped into the bake. This changes item 20 below and integration 2.
- **INCOIS drifting buoys are listed as downloadable** ("Public Access with visualisation, download
  options").
- **`ArgoFloats` came back** later the same day (item 6 is a transient outage, still no fallback).
- **NOAA PSL Godas runs to July 2026** and **IMD's workbook is 1982-2026**; the other pass had both wrong.
- **VAM inputs still unverified**; an INCOIS paper grids Argo only, but it is not tied to the ERDDAP dataset.
- **No free archive of PFZ lines** was found; a price list was reported and could not be verified.

## Part A. Integrations

### Ranked shortlist

| # | Integration | PS audience | New data (access) | Effort | Wow |
| --- | --- | --- | --- | --- | --- |
| 1 | **Fishing-ground water column** | fishery advisories, outreach | Copernicus BGC model + gap-free satellite chl (free login); INCOIS PFZ lines (open WFS) | L | High |
| 2 | **INCOIS's own current instruments score the currents** | search and rescue, forecasters | INCOIS OON portal: HF radar, OMNI ADCP, drifters (no login, permission needed); GTS drifters (open) | M | High |
| 3 | **Marine heatwaves below the surface** | climate monitoring, hazard, outreach | NOAA OISST daily (open); NOAA Coral Reef Watch (open) | M | High |
| 4 | **Scorecard for INCOIS's daily forecasts** | forecasters (the PS's end user) | INCOIS THREDDS rolling files (open) harvested daily | L | Very high |
| 5 | **Wind and waves in the drift model** | search and rescue | Copernicus waves with Stokes drift (free login); winds | M | Medium |
| 6 | **Every storm in the window, day by day** | hazard, outreach | IMD best track / IBTrACS (open); OISST daily; Copernicus waves | M | Medium |
| 7 | Satellite surface salinity | Hilsa, Bay of Bengal | Copernicus MULTIOBS SSS (free login) | S | Low |
| 8 | Coral bleaching heat stress | climate, outreach | NOAA CRW DHW (open) | S | Low (fold into 3) |
| 9 | INCOIS's machine-learning Hilsa map as a Field | the PS's ML clause | INCOIS THREDDS (open, 3 days rolling) | S | Low |

Not recommended: tide gauges and storm surge (coastal, far below a 110 km cell), oil spill (a copy of 5
with nothing to score it against), IMD forecast cones (only found in advisory PDFs; no
machine-readable feed verified).

### How the top four become one story

**"Any INCOIS advisory, opened in 3D, with the instruments that checked it."**

| INCOIS publishes... | The platform opens... | ...and checks it with |
| --- | --- | --- |
| a PFZ line off Kerala | chlorophyll, oxygen, mixed layer and 26 degC depth under the line | BGC-Argo chlorophyll and oxygen |
| a marine heatwave over the Arabian Sea | how deep the warm water goes, against the 1991-2020 normal | Argo floats and moorings |
| a cyclone track | heat potential, waves, the cold wake day by day | moorings and floats near the track |
| a search from a last-known position | drift through currents, wind and waves | HF radar, OMNI current profilers, drifters |

One new concept, the **advisory overlay**, and every existing part gains a job: the 3D block, the
sheets and drapes, the bias map (it gains chlorophyll, oxygen and currents), drift, the section, the
case walkthrough and Explore.

### 1. Fishing-ground water column

**INCOIS need**
- PFZ advisories run daily for 14 coastal sectors with reference to 586 landing centres, built from
  satellite SST and chlorophyll; INCOIS say zones "could shift" and add wind to help
  (incois.gov.in/MarineFisheries/PfzAdvisory, read 2026-09-15).
- INCOIS staff, iScience 29(7):116421, 30 Jun 2026 (doi 10.1016/j.isci.2026.116421): "the lack of
  seamless access to cloud-free satellite data, especially in the near-coastal area during the monsoon
  months, is a major challenge"; they want species-specific advice and better validation. Purse-seine
  catch per haul was 3,260.5 kg inside PFZs against 1,616.2 kg outside.
- INCOIS staff, Frontiers in Marine Science, 26 Aug 2026 (doi 10.3389/fmars.2026.1918530): "To
  transform the advisories into forecasts and develop species-specific predictions of fishery grounds,
  high-quality and high-frequency georeferenced fish catch data over a large spatial scale is essential."
- Species advisories exist: tuna since November 2010 (SST, chlorophyll, Kd490); Hilsa (HiFA) for West
  Bengal, June to September, machine learning at 1/12 degree, operational April 2025 per the iScience
  paper, using SST, salinity and currents.

**Data, tested**
- INCOIS PFZ lines: `https://incois.gov.in/geoserver/PFZ_Automation/ows` WFS, GeoJSON, no login.
  87 lines on 2026-09-15, all Julian day 257 of 2026. **Today's advisory only, no archive** and no
  time dimension in WMS capabilities. Licence not stated.
- Copernicus `GLOBAL_ANALYSISFORECAST_BGC_001_028`, 0.25 degree, 50 levels, daily, 2021-11-01 to
  2026-09-24: `chl`, `phyc`, `o2`, `nppv`, `no3`, `po4`, `si`, `fe`. Free login. Read: oxygen at
  156 m on 2026-07-30 over the box, 10.5 to 191.9 mmol/m3.
- Copernicus `OCEANCOLOUR_GLO_BGC_L4_NRT_009_102` gap-free daily 4 km chlorophyll, 2023-10-01 to
  2026-09-13. Free login. Read for 2026-09-13.
- BGC-Argo in the window (Ifremer ERDDAP, distinct floats with a value flagged 1, 2, 5 or 8):
  chlorophyll 58, oxygen 45, nitrate 27.
- Model against floats, July 2026: see "BGC feasibility check" at the end of Part A.

**How it plugs in**
- Adapters: `sources/copernicus_bgc.py` (GridSource: chlorophyll, oxygen) and `sources/pfz.py`
  (a new overlay source, lines not a Grid).
- Fields: chlorophyll and oxygen as **volume** Fields; "depth where oxygen falls below a threshold" as
  a **depth** sheet (same shape as D26 in `hazard.py`).
- Bias map: `residuals.py` gains chlorophyll and oxygen, collocated in `collocation.py` against the
  BGC floats that today draw one line.
- Overlay: PFZ lines drawn in `OceanScene.ts` with an `ORDER` entry; key in `MapKey.tsx`; guide entries.
- Drift: carry a line forward one day through `drift.ts`, which is exactly the "zones shift" problem.
- Explore / case: "Why do fish gather here?" and a one-day walkthrough in `cases.ts`.

**What it makes possible** - the subsurface picture under a surface advisory, on cloudy monsoon days
too, checked against real floats. No INCOIS tool shows a PFZ line with the oxygen floor under it.

**Limits**
- PFZ lines have no public archive, so they cannot share the current window: harvest daily from now
  (the bake window would have to move forward) or ask INCOIS for an archive.
- 0.25 degree model on a 1 degree platform grid; a front narrower than a cell is lost. Never call
  anything here a PFZ or a forecast.
- The chlorophyll model is a model; the floats are few (58 over a year).

**Effort** L (two adapters, two Fields, an overlay kind, residuals for two new quantities). **Wow** high.

### 2. INCOIS's own current instruments score the currents

**INCOIS need** - SARAT (sarat.incois.gov.in) says "the movement of the missing objects are governed
mainly by the currents and winds", on ROMS currents. The PS names "moorings, HF-radar, ADCP". The
build's drift score today is at 1000 m (Argo parking), not at the surface where people drift.

**Data, tested** (INCOIS Ocean Observation Network portal, `incois.gov.in/OON/`, no login)
- HF radar sites: `fetchHFRadarBuoyData.jsp`, 10 stations in 5 pairs (Gujarat, Tamil Nadu, Andhra
  Pradesh, Odisha, Andaman).
- HF radar dates: `fetchAvailableDates.jsp`, 236 dates, 2026-01-01 to 2026-09-15.
- Vectors: `fetchHFRadarVectors_2025.jsp?date=2026-07-30` returned 2,000 vectors (looks capped) for
  six hours, speed and direction; units not stated (values read as cm/s: median 23, 95th percentile 86).
- OMNI moorings: GeoServer WFS `JointPortal:Omni_Buoy`, 12 buoys, each with an `EEZ_Status` flag
  (3 inside the EEZ). Buoy page `moored_omnidata_stock.jsp?buoy=AD07&parameter=adcp_speed_015m`
  embeds hourly values 2012-10-22 to 2026-08-03 (433 hours inside the window at 15 m); temperature at
  50 m runs to 2026-09-15. Parameters offered: currents at 1.2 to 100 m, temperature and salinity to 500 m.
- Drifters: `backend_process.jsp` (POST) listed 10 INCOIS drifters over 20-30 Jul 2026; NOAA OSMC lists
  17 drifting buoys in the box in July 2026. OSMC carries no current columns here (no rows Jan-Jul 2026).
- Terms: INCOIS staff state a request form applies to every user and EEZ data is generally restricted
  (Data Science Journal 2018, doi 10.5334/dsj-2018-011). These are web-app endpoints, not a documented API.

**How it plugs in** - `sources/incois_oon.py` (ProfileSource for OMNI T/S; a new current-observation
source); `drift.py` scores the Copernicus field against HF radar and drifters at the surface;
`residuals.py` gains a current residual; the bias map shows where the current field is wrong.

**One-day feasibility** - on 30 Jul 2026, 11 one-degree cells hold both HF radar vectors and baked
Copernicus currents. That proves overlap, not skill: six hours, direction convention not confirmed.

**Limits** - permission first; HF radar reaches about 200 km offshore, a few cells of this grid;
2026 only; ADCP series have long gaps.

**Effort** M. **Wow** high: the current model scored against India's own radars.

### 3. Marine heatwaves below the surface

**INCOIS need** - Marine Heatwave Advisory Services (incois.gov.in/oceanservices/mhw/index.jsp):
on 2026-09-13, "Moderate to Extreme" heatwaves covering 57.90% of the Arabian Sea and 53.77% of the
Bay of Bengal. SOP: NOAA OISST, 90th percentile of a 1991-2020 daily climatology (11-day window),
five days or more, Hobday categories. Surface only.

**Data, tested** - NOAA OISST v2.1 daily via NOAA PSL THREDDS (open), 2026 file to 2026-09-13.
**The PSL anomaly file is against 1971-2000**, not 1991-2020, so the baseline must be built from the
daily means. NOAA Coral Reef Watch DHW (coastwatch.noaa.gov ERDDAP) to 2026-09-12, 5 km.

**How it plugs in** - `climatology.py` (a daily 1991-2020 percentile baseline); a **column** drape for
heatwave category; the existing Temperature vs Normal volume answers "how deep" with the same base
period; floats and moorings check it; Explore question; guide entries.

**Limits** - OISST is surface only; the analysis is 10-daily and cannot resolve a five-day event
below the surface; a year is not a trend.

**Effort** M. **Wow** high, and topical this week.

### 4. Scorecard for INCOIS's daily forecasts

**INCOIS need** - the PS's end product is "improving the speed and accuracy of operational advisories".

**Data, tested** - `https://incois.gov.in/thredds/catalog.xml` now lists GODAS, ROMS, HYCOM and
Ocean State Forecast catalogues. OPeNDAP `.dds` read for: HOOFS surface currents (1080 x 720, 32
steps), WW3 waves (SWH, swell, periods), winds, GODAS TCHP, HYCOM TCHP (46 steps), storm surge.
Rolling files only: two to four days kept.

**How it plugs in** - a scheduled harvester stores each forecast; three to ten days later it is
collocated against floats, moorings, drifters and HF radar through the existing `collocation.py` and
`drift.py`; a scorecard page. **Limits** - no history for the current window; storage in git grows.
**Effort** L. **Wow** very high.

### 5. Wind and waves in the drift model

Copernicus `GLOBAL_ANALYSISFORECAST_WAV_001_027`, 1/12 degree, 3-hourly, 2022-11-01 to 2026-09-24,
with Stokes drift `VSDX`/`VSDY` (read at 00 UTC 28 Oct 2025: wave height up to 5.96 m, Stokes drift up
to 0.45 m/s). Plugs into `drift.py`/`drift.ts`, scored against drifters (item 2). Limit: a leeway
factor per object is literature, not SARAT. Effort M.

### 6. Every storm in the window, day by day

IBTrACS North Indian (NCEI, open, 27.9 MB) holds Shakhti (Arabian Sea, Oct 2025, 60 kt), Montha,
Senyar and Ditwah (Nov-Dec 2025) with IMD as agency, marked provisional; IMD's own workbook
(1982-2026) downloaded (9.8 MB). Daily OISST and Copernicus waves resolve the cold wake that 10-day
analyses cannot. Plugs into `storm.py`, `build_montha_case.py`, `cases.ts`. Effort M.

### 7 to 9, briefly

- **Surface salinity** - Copernicus `MULTIOBS_GLO_PHY_S_SURFACE_MYNRT_015_013` to 2026-09-09. The Bay
  of Bengal plume at the surface, beside the analysis. Small.
- **Coral heat stress** - fold into 3.
- **HiFA** - `thredds/dodsC/hilsa/HiFA_Latest_File.nc`: 3 days, 222 x 334 cells, categories. It lives in
  about two cells of the platform grid. Answers the ML clause by showing INCOIS's own ML product, not
  by training one.

### BGC feasibility check (July 2026)

Every BGC-Argo cast in the box, 1-30 Jul 2026, with a good flag (1, 2, 5 or 8), against the
Copernicus BGC model at the nearest cell and day. Pressure taken as depth within 10 m; oxygen
converted from umol/kg with 1025 kg/m3. Typical gap = median absolute difference.

| Depth | Oxygen float / model median (mmol/m3), 76 casts, 26 floats | Gap | Chlorophyll float / model median (mg/m3), 119 casts, 40 floats | Gap |
| --- | --- | --- | --- | --- |
| 10 m | 196 / 200 | 4 | 0.08 / 0.22 | 0.12 |
| 50 m | 195 / 199 | 6 | 0.18 / 0.35 | 0.21 |
| 100 m | 95 / 123 | 35 | 0.13 / 0.31 | 0.17 |
| 150 m | 55 / 69 | 19 | 0.02 / 0.05 | 0.04 |
| 300 m | 70 / 66 | 7 | 0.01 / 0.01 | 0.01 |
| 500 m | 53 / 55 | 6 | 0.02 / 0.00 | 0.01 |

- Oxygen is close at the surface and at depth; the model holds too much at 100-150 m, where oxygen
  drops away - the depth that squeezes fish habitat, so the bias map would show something real.
- Chlorophyll: the model reads about twice the floats in the top 100 m.
- One month, one model, nearest-cell matching: a feasibility check, not a score.
- All 155,931 rows had `position_qc` and `time_qc` of 1, so dataset check 7 did not bite this month.

---

## Part B. Dataset verification

Verdicts: HOLDS, PARTLY, WRONG, RISK (works but fragile), UNVERIFIED.

| # | Assumption | Verdict | Evidence, 2026-09-15 | Fix |
| --- | --- | --- | --- | --- |
| 1 | VAM: 24 levels 5-2000 m, 1 degree, 60 x 90, to 2026-07-30 | HOLDS | ERDDAP info: 813 steps, 2004-01-10 to 2026-07-30, history "FERRET V6.7 14-Aug-26"; no step after 30 Jul yet | `00-data-sources-verified.md` says start 2004-01-15; metadata says 2004-01-10 |
| 2 | McCreary: same grid, with RMSE and counts, to 2026-07-30 | HOLDS | 921 steps from 2001-01-10; T and S ANALYZED, MEAN, STDEV, RMSE, ROIOBS, BOXOBS; merged 17 Aug 2026 | - |
| 3 | Value-added series ends 2019-03-30 | HOLDS | 549 steps, 2004-01-10 to 2019-03-30 | - |
| 4 | The VAM analysis does not ingest moored buoys | UNVERIFIED | ERDDAP metadata names no inputs. Jha and Udaya Bhaskar (INCOIS), J. Earth Syst. Sci. 2021, grid Argo profiles with DIVA. INCOIS-GODAS **does** assimilate RAMA and NIOT moorings (incois.gov.in/site/datainfo/modelling/godas.jsp) | Say "INCOIS's Argo analysis (VAM)", never "INCOIS"; say "grid", not "assimilate". The bias panel in the running build still says "INCOIS assimilate Argo" |
| 5 | INCOIS's Argo archive ends 2025-04-23 | HOLDS | `Indian_ARGO_Floats` time_coverage_end 2025-04-23T13:28:00Z | - |
| 6 | Ifremer `ArgoFloats` is the live Argo source | RISK | First read 200 (time_coverage_end 2026-12-27, a future date); three later reads 404 "Currently unknown datasetID", and absent from the dataset index (54 datasets) | Add a fallback: the Argo GDAC FTP index (updated 2026-09-15 05:24 UTC) or `ArgoFloats-index` |
| 7 | Argo QC: flags 3, 4, 9 refused per value | PARTLY | Value flags are read (`argo.py`); `position_qc` and `time_qc` exist in the dataset and are not requested | Request both and refuse a cast whose position or time flag is 3, 4 or 9 |
| 8 | 57 floats carry chlorophyll | HOLDS | 58 distinct floats with a good-flag `chla_adjusted` in the window; the bake keeps 57 after pairing | - |
| 9 | No usable BGC oxygen (`argo.py` BgcArgoSource note) | WRONG | 45 floats with `doxy_adjusted` flagged 1 or 8 in the window; nitrate 27 | Update the note; the old count was for the 12-step window |
| 10 | No gridded chlorophyll shares this timeline (`argo.py`, README-full) | WRONG | Copernicus BGC model chl 2021-11-01 to 2026-09-24; gap-free satellite chl 2023-10-01 to 2026-09-13 | "INCOIS's own ocean-colour series end in 2006 and 2020; Copernicus publishes chlorophyll on this timeline behind a free account, not yet read" |
| 11 | Oxygen refused because only a decadal climatology exists (ADR 0010) | WRONG now | Copernicus BGC `o2`, daily, 0.25 degree, covers the window | Amend ADR 0010 as history |
| 12 | Copernicus currents dataset covers the window | HOLDS | `cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m_202406`: uo, vo, 50 levels, 2022-06-01 to 2026-09-24 | - |
| 13 | PS reanalysis 001_030 ends 2026-06-23 | HOLDS | STAC 1993-01-01 to 2026-06-23; product page 200 | - |
| 14 | OSMC moorings, CC0, no current columns | HOLDS | Licence text waives rights; 8 moorings with subsurface temperature in July 2026; no `uo` rows Jan-Jul 2026 | - |
| 15 | WOA23 read over OPeNDAP | RISK | `.dds` 503 after 62 s (timed out 2026-09-14); HTTPS file 200, 60.5 MB, modified 2024-01-29 | Cache the 12 monthly subsets in `data/`, or fall back to HTTPS |
| 16 | Glider: 2,876 casts in box, newest 2022-10-14 | HOLDS | Full index streamed: 248,440,873 B, 824,632 rows, 2,876 in box, newest 20221014050357, 0 after | - |
| 17 | Argo FTP named by the PS is live | HOLDS | `ftp.ifremer.fr/ifremer/argo` 22 entries; `ar_index_global_prof.txt` modified 2026-09-15 05:24 UTC | - |
| 18 | LAS: catalogue reads, data does not | HOLDS | Root 200; THREDDS catalogue 59 entries; `getDatasets.do` 17.0 MB; OPeNDAP `.dds` timed out at 90 s | - |
| 19 | IMD best track | HOLDS | Workbook 1982-2026, 9.8 MB, sheets to 2026; IBTrACS NI v04r01 also holds Montha (provisional) | - |
| 20 | "India's HF-radar and ADCP are not open" (requirements page, README-full) | WRONG | OON portal serves HF-radar vectors (1 Jan to 15 Sep 2026) and OMNI ADCP hourly series with no login | "INCOIS shows HF-radar and mooring current data on its public observation portal, but publishes no download API and restricts EEZ data by policy, so the build does not read it yet" |
| 21 | `incois.gov.in/thredds` is an unconfigured, empty install (`00-data-sources-verified.md`) | WRONG | Catalogue lists GODAS, ROMS, HYCOM, OSF currents, winds, waves, SST, chl, storm surge; title still the default | Record as rolling operational files, 2-4 days |
| 22 | `services.incois.gov.in` unreachable | HOLDS | Connect failed after 21 s | - |
| 23 | INCOIS still publish TCHP | HOLDS | GODAS `tchp_20260913.nc`, HYCOM `hycom_tchp.nc` (46 steps) on THREDDS | - |
| 24 | PS: deadline 30 Sep 2026; item d blank | HOLDS | sih.gov.in/sih2026PS row "SIH26067 ... 30 September 2026"; dataset text unchanged | - |
| 25 | AOML 6-hourly drifters end 2025-06-18 | HOLDS | time_coverage_end 2025-06-18T12:00:00Z | - |
| 26 | INCOIS ERDDAP holds 18 datasets | PARTLY | 17 datasets plus the `allDatasets` index; `AMSR2_3day_Global` shows a broken time axis (1901 to 1915) | Say 17 |

### Not verified

- VAM input data (item 4).
- HF radar units and direction convention; whether the 2,000-row response is a cap.
- IMD forecast tracks and cones in machine-readable form.
- The 2026 sheet of IMD's workbook was not parsed.
- NOAA's own Godas (checked 2026-09-14 only).
- Ifremer `ArgoFloats` recovery after the 404s.

## Sources

INCOIS: PfzAdvisory, TunaAdvisory, oceanservices/mhw (and SOP PDF), oceanservices/Hilsa, site/services/hab,
coralReef, datainfo/modelling/{godas,hycom,ecosystem}, OON portal and its JSON endpoints, GeoServer WFS
(PFZ_Automation, JointPortal, Insitu_TideGauges_Tsunami), THREDDS catalogue, ERDDAP, LAS, SARAT, OOSA.
Papers: Lal et al. 2026 iScience doi 10.1016/j.isci.2026.116421; Lal et al. 2026 Front. Mar. Sci. doi
10.3389/fmars.2026.1918530; Chakraborty et al. 2019 J. Oper. Oceanogr. doi 10.1080/1755876X.2019.1574951;
Jha and Udaya Bhaskar 2021 J. Earth Syst. Sci. doi 10.1007/s12040-021-01675-2; Data Science Journal 2018
doi 10.5334/dsj-2018-011. Copernicus STAC records for 001_024, 001_028, 001_030, WAV_001_027,
OCEANCOLOUR 009_102, SEALEVEL 008_046, MULTIOBS 015_013. NOAA PSL OISST, NOAA CRW ERDDAP, NOAA OSMC and
AOML ERDDAP, NCEI WOA23 and IBTrACS, IMD RSMC New Delhi, sih.gov.in.
