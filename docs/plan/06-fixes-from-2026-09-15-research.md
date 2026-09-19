# Fixes and next steps from the 15 September 2026 research

**Status, 2026-09-19: section 6 items 1 to 6 done and pushed (9f783e7, 57fc2cd, ca8ab50); item 7
not started.** See "Still open" at the end. What changed and what was left is at the end of this file, under "Done". Read this file, then the research note it rests
on: [`docs/research/2026-09-15-integrations-and-datasets.md`](../research/2026-09-15-integrations-and-datasets.md).
The plain-language brief for the owner is the artifact
https://claude.ai/artifact/TncqufHwDyhvi1rzqHBSEH (not in the repo).

Standing rules still apply: verify before claiming, no em dashes, run `pytest`, `check_figures.py`
and the probes that touch what you change, and **never commit or push unless the owner says so.
When the owner says "commit", that means commit and push.**

---

## 1. What was verified after the first research pass (15 Sep 2026, evening)

A second, independent research pass was run by another AI. Every claim below was re-checked from
the build machine; claims that did not survive are listed as wrong.

| Question | Verified answer | Evidence |
| --- | --- | --- |
| Can the build use INCOIS OMNI moored buoy data from the portal? | **No, not without a request.** INCOIS list moored buoy data as view-only | `incois.gov.in/site/dataholdings.jsp`: "Moored Buoy ... Profiles of Temperature, Salinity up to 500 m and Currents up to 100m ... Public Access with only visualisation option" (the row continues "No download option" per the other research) |
| HF radar access? | **Registered access**, not open | Same page: "HF Radar \| Current Vector \| Real-time \| 2008 - till date \| Registered access through Website" |
| INCOIS drifting buoys? | **Downloadable** | Same page: "Drifting Buoy \| Atmospheric Pressure, SST, Ocean Currents \| ... Public Access with visualisation, download options" |
| Tide gauges, tsunami buoys, BPR | View-only on the tsunami centre site | Same page: "Visualization. No download facility" |
| Ifremer `ArgoFloats` outage | **Transient.** 404 three times around 11:10-11:33 IST, back to 200 later the same day, with `position_qc` and `time_qc` listed | `erddap.ifremer.fr/erddap/info/ArgoFloats/index.csv` |
| NOAA PSL Godas latest month | **July 2026** (the other research's "December 2025" was wrong) | `downloads.psl.noaa.gov/Datasets/godas/`: `pottmp.2026.nc` modified 2026-08-17; OPeNDAP time axis has 7 monthly values |
| IMD best track workbook | **1982-2026** (the other research's "only to 2025" was wrong) | `rsmcnewdelhi.imd.gov.in/report.php?internal_menu=MzM=` lists "Best Tracks Data (1982-2026)"; file downloaded, has a `2026` sheet |
| VAM analysis inputs | **Still unverified.** Leaning Argo-only | Jha and Udaya Bhaskar (INCOIS), J. Earth Syst. Sci. 2021, doi 10.1007/s12040-021-01675-2: "temperature and salinity profiles data obtained from Argo profiling floats were used" - but that paper names DIVA, and nothing ties it to the ERDDAP dataset `incois_argo_10d_VAM`. INCOIS Data Holdings still lists the VAM product as "2002 - 2013" (stale) |
| HF radar official route | Request through INCOIS (reported, not re-checked) | Jena et al. 2019, Current Science, "Indian Coastal Ocean Radar Network": "ICORN provides data to the researchers on a request basis through INCOIS" |
| OMNI official route | Request through INCOIS (reported, not re-checked) | MoES Earth System Science Data Portal: "INCOIS has been identified as the Data Centre to provide the moored buoy data to the users on request" |
| PFZ line archive | **No public archive.** A price list for PFZ spatial data was reported and **could not be verified** (`services.incois.gov.in` unreachable). Treat past PFZ lines as unavailable: the owner's rule is no paid data | `incois.gov.in/MarineFisheries/TextDataHome` shows only the current forecast date |
| IMD forecast tracks and cones | Images and PDFs only; no KML, shapefile or CSV found | RSMC New Delhi archive pages |
| WOA23 OPeNDAP retirement | No retirement notice found; OPeNDAP still returned 503 on 15 Sep | NCEI WOA23 pages list THREDDS and HTTPS |

**Consequence for the plan:** the idea "INCOIS's own current instruments score the drift model"
now needs a formal data request for HF radar and OMNI. INCOIS drifting buoys are the one INCOIS
current source listed as downloadable. **Do not scrape the portal's embedded buoy series or HF-radar
JSON into the bake** - INCOIS classify that data as view-only or registered access.

---

## 2. Wording fixes (claims that are wrong today)

### 2a. "INCOIS assimilate Argo" and "the buoys are independent"

The VAM analysis is gridding (objective or variational analysis), not data assimilation into a
model, and whether it excludes buoys is unverified. INCOIS-GODAS does assimilate RAMA and NIOT
moorings (`incois.gov.in/site/datainfo/modelling/godas.jsp`). Replace "INCOIS assimilate Argo" with
wording that names the analysis and says it is built from Argo, for example: *"INCOIS's gridded Argo
analysis is built from these floats, so a float largely shows the analysis agreeing with data it
was made from. The moored buoys are not described as inputs, which makes them the closer thing to
an independent check."*

Locations (from a grep on 15 Sep 2026; re-grep before editing):
- `README.md:68`, `README.md:187`
- `docs/README-full.md:71`, `:189-190`
- `web/index.html:810`
- `web/src/explore.ts:125-126`
- `web/src/guide.ts:880`
- `web/src/ui/Controls.tsx:466`, `:501-502`, `:533` (the live bias panel text)
- `web/src/ui/ProfilePanel.tsx:250`, `:256`
- `web/src/types.ts:365-366`
- `pipeline/samudra/residuals.py:27-28`, `:178`, `:288`
- `pipeline/samudra/bake.py:415`, `:1588-1589`
- `pipeline/tests/test_residuals.py:406`, `:422` (docstrings)
- `CLAUDE.md:390-391`, `PRODUCT.md:55`
- `scripts/dossier.html:362`, `docs/demo/script.md:62-63`, `ppt/NOTES.md:100`, `ppt/PLAN.md:36`
- `ppt/script.md:175` is the **locked video script**; leave it (see `docs/NUMBERS.md`)
- History files (`docs/plan/02`, `docs/BUGS.md`, `docs/landing-alternatives/`) stay as history

### 2b. HF radar and ADCP "not open"

New wording: *"INCOIS lists HF-radar data as registered access and moored-buoy currents as
view-only, so using either needs a data request to INCOIS. A data-policy limit, not a design gap."*
Drop the `services.incois.gov.in` sentence (it adds nothing now).

- `web/requirements.html:596`, `:599`, `:737-739`
- `docs/README-full.md:345` (long line, the extensible-design row), `:353`, `:403`, `:683`
- History: `docs/plan/01-cut-features.md:44`, `docs/plan/03-requirement-gaps.md:240-243`,
  `docs/plan/04-ps-update-2026-09.md:322` - add a dated note rather than rewriting

### 2c. "No gridded chlorophyll shares this timeline" and "no usable oxygen"

Copernicus `GLOBAL_ANALYSISFORECAST_BGC_001_028` (chl, o2, daily, 0.25 degree, 2021-11-01 to
2026-09-24) and the gap-free satellite chlorophyll `OCEANCOLOUR_GLO_BGC_L4_NRT_009_102`
(2023-10-01 to 2026-09-13) both cover the window. 45 BGC-Argo floats in the box carry
`doxy_adjusted` flagged 1 or 8. New wording until integration 1 is built: *"INCOIS's own
ocean-colour series end in 2006 and 2020. Copernicus publishes chlorophyll for this period behind a
free account; this build does not read it yet."*

- `web/src/ui/ProfilePanel.tsx:327`, `:412`
- `web/src/guide.ts:896`
- `web/src/types.ts:444`
- `pipeline/samudra/sources/argo.py:175-181` (oxygen count note), `:252` (docstring)
- `pipeline/samudra/bake.py:370`, `:388`, `:1793`
- `pipeline/tests/test_residuals.py:116` (docstring only)
- `docs/README-full.md:279`
- ADR 0010 line 21 and `docs/plan/01-cut-features.md:41`: add a dated amendment, do not rewrite

### 2d. `incois.gov.in/thredds` "unconfigured, no datasets"

- `docs/plan/00-data-sources-verified.md:74-75`: add that on 2026-09-15 it served rolling
  operational files (GODAS, ROMS, HYCOM, OSF currents, winds, waves, SST, chlorophyll, storm surge),
  two to four days each.

### 2e. Small corrections

- `docs/plan/00-data-sources-verified.md:40`: VAM starts 2004-01-10 (ERDDAP metadata), not 2004-01-15.
- `docs/plan/00-data-sources-verified.md:136`: INCOIS ERDDAP holds 17 datasets plus the
  `allDatasets` index, not 18.
- `manifest.json` still says "RAMA array is a joint MoES-NOAA programme" (known from part 17;
  fixed only by a bake or `refresh_field_prose.py`-style script).

---

## 3. Robustness fixes (code)

1. **Argo position and time QC.** `pipeline/samudra/sources/argo.py` requests value flags only.
   Add `position_qc` and `time_qc` to `ProfileColumns.request()` and refuse a cast flagged 3, 4 or 9.
   TDD: a parser test with a flagged position. (In July 2026 every row was flagged 1, so no figure
   should move; check with `collect_facts.py`.)
2. **No fallback for Ifremer `ArgoFloats`.** It went down for part of 15 Sep. Options: retry with
   backoff in `fetch_profiles`, or a fallback through `ArgoFloats-index` / the GDAC FTP index.
3. **WOA23 OPeNDAP returns 503.** `pipeline/samudra/sources/woa.py` reads only OPeNDAP. Cache the
   12 monthly regional subsets under `data/` (server-side, like `data/glider/`) or fall back to the
   HTTPS file server (`www.ncei.noaa.gov/data/oceans/woa/WOA23/...`, 60.5 MB per month).

---

## 4. The integration plan, in the owner's words

Recommended first build: **show the water under INCOIS's fishing zones** (full detail in the
research note, Part A, item 1, and the artifact). Five steps, each useful alone:

1. Copernicus plankton (chl) and oxygen as two new volume Fields (`sources/copernicus_bgc.py`).
2. Collocate them against BGC-Argo floats, so the bias map gains chlorophyll and oxygen
   (`collocation.py`, `residuals.py`, `ProfilePanel.tsx`).
3. An "oxygen floor" depth sheet (same shape as D26 in `hazard.py`).
4. INCOIS PFZ lines as an overlay (`sources/pfz.py`, `OceanScene.ts` with an `ORDER` entry, `MapKey.tsx`).
5. An Explore question and a walkthrough (`explore.ts`, `cases.ts`), with guide entries.

July 2026 feasibility check (research note, "BGC feasibility check"): oxygen matches floats near the
surface and at depth but is too high at 100-150 m; the model's chlorophyll is about twice the floats'
in the top 100 m.

Later ideas, in order: INCOIS current instruments score drift (needs the data request); marine
heatwaves below the surface (NOAA OISST, build a 1991-2020 daily baseline - the PSL anomaly file is
1971-2000); a scorecard for INCOIS's daily forecasts; wind and waves in drift; every storm in the
window.

## 5. Decisions taken by the owner, 15 Sep 2026

1. **No data request to INCOIS.** HF radar and OMNI buoy data are out. The "INCOIS instruments
   score drift" idea may only use INCOIS drifting buoys (listed as downloadable) or GTS drifters.
2. **PFZ lines: no archive, so two things instead.**
   - **Fronts for the whole window, computed here** from Copernicus satellite SST
     (`SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001`, OSTIA) and gap-free chlorophyll
     (`OCEANCOLOUR_GLO_BGC_L4_NRT_009_102`), following INCOIS's published method (thermal fronts by
     Cayula and Cornillon 1992, chlorophyll fronts by Canny). **Labelled "fronts, the ingredient
     INCOIS builds fishing zones from", never "fishing zones".** Replaces step 4's overlay for the demo.
   - **A small daily harvester** saving INCOIS's PFZ WFS lines from now on, for a later window.
     Not part of the current bake.
3. **Tour and walkthrough bug.** Owner report: during "Show me around" or a walkthrough started
   from Explore, touching any left-panel control closes it. Cause: `web/src/store.ts:627-634`
   nulls `tourStep` and `caseStep` whenever `touched` is set, on purpose. Wanted: **pause instead of
   close** - the card stays with "Continue" (restores that step's scene) and "End". Update
   `probe-tour.mjs`, `probe-case.mjs` (they assert that touching ends it), possibly
   `probe-outreach.mjs`, and the rule text in `CLAUDE.md` / `web/CLAUDE.md`.
4. **README video note.** The prototype video is already recorded:
   https://drive.google.com/file/d/1LTY8K1G6kZmPgNEslfE59tnTUSqkIc29/view . Add a short line to
   `README.md` linking it and saying which features are not in it because they were built after it.
   `ppt/script.md` was last changed 2026-09-09; commits after that added the Cyclone Montha
   walkthrough, the cyclone fields checked against INCOIS's archive, and the requirements and
   provenance page redesigns. **The owner confirmed (15 Sep) all three were made after the video.**
   Add the new features from this plan to the list once they exist.

## 6. Order of work agreed

1. Tour and walkthrough pause fix.
2. Wording fixes (section 2) and the README video line.
3. Robustness fixes (section 3), before any bake.
4. Fishing water column: plankton and oxygen Fields, collocation against BGC floats, oxygen floor
   sheet; fronts Field from satellite SST and chlorophyll. Then **one** bake.
5. Explore question, walkthrough, guide entries, tour steps for everything new.
6. After the bake: `collect_facts.py`, `check_figures.py`, screenshots, deck figures, README line updated.
7. Later: PFZ harvester, marine heatwaves below the surface, forecast scorecard, wind and waves in drift.

## Done, 2026-09-15 (committed 2026-09-19)

1. **Pause, not close.** A touch sets `cardPaused`; the card offers Continue and End. Both probes check it.
2. **Wording.** 2a, 2b, 2d, 2e done; history files got dated notes. 2c was done inside item 4, because
   chlorophyll and oxygen gained a model side and the interim sentence would have been wrong at once.
   Left as they were: `ppt/script.md` (locked), `ppt/DECK.md`, `ppt/NOTES.md`, `scripts/dossier.html`,
   `scripts/ppt_diagrams.html` test and probe counts, as `docs/NUMBERS.md` already records.
3. **Robustness.** Argo `position_qc`/`time_qc` (INCOIS: `JULD_QC`, no position flag); Argo retry with
   backoff, about 17 minutes, not on "no matching results"; WOA23 reads `data/woa/` first, then OPeNDAP,
   then HTTPS, and all twelve months are saved there.
4. **Biology.** Chlorophyll and oxygen Fields (Copernicus BGC), collocated against BGC-Argo and on the
   bias map; Oxygen Floor sheet; Surface Fronts drape. ADR 0018. One 36-step bake.
   **Correction to the research note:** the near-real-time gap-free chlorophyll
   (`OCEANCOLOUR_GLO_BGC_L4_NRT_009_102`) keeps only nineteen days (2026-08-26 to 2026-09-13); the
   multi-year product `OCEANCOLOUR_GLO_BGC_L4_MY_009_104` covers the window and is what is read.
5. Explore question "Why do fish gather here?", a fishing walkthrough (`?case=fishing`), four guide
   entries, one tour step (22 steps, 47 entries).
6. `collect_facts.py` (new Biology section), `check_figures.py`, figures updated in current documents.
   Screenshots shot into `web/shots/biology-2026-09-15/`, not published.

Found on the way: Ifremer's `ArgoFloats` no longer returns floats 5907083 and 7901128 for this
window, so the bake has 257 floats, not 259. Upstream, not the new QC.

## Done, 2026-09-19

- **Fronts palette.** `turbid` (pale yellow to dark brown) hid the orange float tracks: closest
  colour difference 19.5 CIE76 on dark, 25.6 on light. Now reversed `ice` (pale blue to
  near-black): 69 and 83. Applied with `refresh_palettes.py`, which now also re-points a Field's
  `palette` from its `FieldSpec` and refuses a change into or out of a diverging or banded palette.
  No bake.
- **Stale figures.** `check_figures.py` reports 0 current. Also removed "CI runs both on every
  push" from `ppt/DECK.md` (CI typechecks and builds only) and "INCOIS stopped publishing in 2019"
  from the deck and dossier. Dossier PDF and `technical-approach.png` re-rendered.

## Still open, 2026-09-19

- **Screenshots.** Twelve frames of the Biology views in `web/shots/biology-2026-09-15/` (fronts
  frames there show the old palette, so re-shoot those). Nothing ingested or published; the owner
  chooses before any `capture.mjs --publish`.
- **Item 7** of section 6. Deliberately after the 30 September submission.
