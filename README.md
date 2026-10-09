<div align="center">

# OceanVerity

**Fly into the Indian Ocean and see, in one picture, what the model predicted
and what the instruments in the water actually measured.**

[![Launch the platform](https://img.shields.io/badge/Launch-the%20platform-0f766e?style=for-the-badge&logo=googleearth&logoColor=white)](https://rak2315.github.io/oceanverity/app.html)
[![Landing page](https://img.shields.io/badge/Landing-page-0891b2?style=for-the-badge)](https://rak2315.github.io/oceanverity/)
[![Provenance](https://img.shields.io/badge/Every%20figure-sourced-155e75?style=for-the-badge)](https://rak2315.github.io/oceanverity/provenance.html)

![Smart India Hackathon 2026](https://img.shields.io/badge/Smart%20India%20Hackathon-2026-FF6F00?style=flat-square)
![Problem Statement 26067](https://img.shields.io/badge/Problem%20Statement-26067-1565C0?style=flat-square)
![MoES / INCOIS](https://img.shields.io/badge/MoES-INCOIS-00695C?style=flat-square)
![Category Software](https://img.shields.io/badge/Category-Software-5E35B1?style=flat-square)
![Theme Disaster Management](https://img.shields.io/badge/Theme-Disaster%20Management-C62828?style=flat-square)
![Team Sigmoid](https://img.shields.io/badge/Team-Sigmoid-37474F?style=flat-square)

![Tests](https://img.shields.io/badge/tests-511%20passing-2ea043)
![Probes](https://img.shields.io/badge/browser%20probes-16%20green-2ea043)
![Network calls at demo time](https://img.shields.io/badge/network%20calls%20at%20demo%20time-0-2ea043)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Three.js](https://img.shields.io/badge/three.js-WebGL2-000000?logo=threedotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST-009688?logo=fastapi&logoColor=white)

<img src="docs/images/collocation.jpg" width="880" alt="The platform running: a three-dimensional block of Indian Ocean water from 5 m to 2000 m with Argo float markers across the top, the control panel on the left, and on the right a chart plotting one float's measured temperature against the model's down the same depth axis.">

*One frame, and the whole idea. INCOIS's own ocean analysis as a block of water you fly into,
the floats drawn where they actually were, and one float's measurement scored against the model:
**1016 depths compared, 0.10 °C average gap, "close agreement"**.*

</div>

---

## In one minute

India runs an **ocean model** - a computed picture of temperature, saltiness and currents all the
way down. India also has **robot floats and anchored buoys** drifting in that same water, taking
real measurements.

Until now you could look at one or the other. Not both, in the same place, at the same depth, on
the same day.

**OceanVerity puts them together.** It draws the ocean as a solid block of water you can fly
inside, from the surface down to two kilometres, with every instrument sitting in it exactly
where it was. Click one and you see what it measured, what the model predicted, and how close the
two came.

It opens in an ordinary browser. Nothing to install, no account, no licence. **It works with the
internet switched off**, because the data travels with the page.

---

## What makes it different

**1. Every number arrives with its accuracy attached.** The platform compares the model against
all **274 instruments** in the water and prints the result. Across them the model sits within
about a quarter of a degree of what was measured, which is a genuinely good analysis - and
because the floats feed the model while the **17 anchored buoys** do not, the two are reported
separately, each with the depth range it covers. A forecaster can see at a glance not just what
the model says but how much to trust it, here, today.

**2. Every value you read is the real one.** The block on screen is a compressed copy built for
the graphics card. Every number a person or another program can obtain - the value under the
cursor, the comparison chart, a vertical slice, an API response - is read from the full-precision
data instead. The picture is for looking at; the numbers come from the source.

**3. It shows you where the evidence is.** One of the 19 variables exists purely to show how many
real measurements stand behind each part of the ocean. About a tenth of the block has none, and
that is drawn rather than filled in - which doubles as a map of where the next float would be
worth deploying.

**4. It has a door for everyone.** Nineteen variables is the right toolkit for a forecaster.
`Explore` turns the same platform into **nine plain questions** for students, the public and
policymakers, and `?kiosk=1` runs it unattended on an exhibition screen all day.

---

## The numbers

Every figure here is read off the running build by a script. Nothing is typed by hand.

| | |
| --- | --- |
| Instruments in the water | **274** - 257 Argo floats + 17 moored buoys |
| Variables | **19**, in 6 groups; 4 published by INCOIS, 2 by Copernicus Marine, 13 computed here |
| Analyses | **36** timesteps, 10 Aug 2025 to 30 Jul 2026, over 45-100 °E and 10 °S-25 °N |
| Depth | **5 m to 2000 m** across 24 uneven levels |
| Data shipped in the build | **223 MB**, committed, **0** network calls to run |
| Source adapters | **11** - 10 providers, plus one for a file a visitor drops on the page |
| Tests / browser probes | **511** / **16** |
| Cyclone fields, validated | agree with INCOIS's own published archive in **97%** of 257,548 cells, across 183 dates from 2004 to 2019 |
| Drift model, scored | median **41 km** out over a ten-day Argo cycle, across 6,185 cycles on 217 floats |

---

## What it looks like

| | |
| --- | --- |
| <img src="docs/images/volume.jpg" width="420" alt="The ray-marched volume: the full ocean depth as one solid body of water."> | <img src="docs/images/anomaly.jpg" width="420" alt="The ocean block drawn as a temperature departure, with rings marking each body of unusual water."> |
| **The water column.** The whole depth as one body, not a stack of slices. | **Unusual water, found for you.** Every departure gets a ring and a panel explaining it. |
| <img src="docs/images/hazard.jpg" width="420" alt="Cyclone heat potential draped on the sea surface in deep reds."> | <img src="docs/images/drift.jpg" width="420" alt="A pin dropped in the Arabian Sea with the track the analysed currents imply running away from it."> |
| **Cyclone mode.** One press swaps in the five things a cyclone forecaster asks of the water. | **Drift.** Drop a pin, follow the current. The model comes with its own measured error. |
| <img src="docs/images/coverage.jpg" width="420" alt="The ocean block drawn as observation coverage in four flat colour bands."> | <img src="docs/images/section.jpg" width="420" alt="A vertical section cut along a drawn line, with float casts overlaid."> |
| **Where the evidence is.** How many real measurements stand behind each part of the water. | **Vertical section.** Draw a line, cut the ocean along it. |
| <img src="docs/images/upload.jpg" width="420" alt="A visitor's own NetCDF file drawn as a block of water, with its own tab in the variable list."> | <img src="docs/images/kiosk.jpg" width="420" alt="The exhibition screen: no panels, one large caption over the water."> |
| **Bring your own data.** Drop a NetCDF file on the page and it draws like everything else. | **Exhibition mode.** The same platform, for a room full of students. |

*Every picture is the running build. Nothing is a mockup and nothing is retouched.*

---

## How it works

**Ten public sources become one common form. That form splits in two: the exact numbers, and a
compressed copy for the graphics card.** Everything anyone reads comes from the exact side.

```mermaid
flowchart LR
    S1["INCOIS<br/>ocean analysis"]
    S2["Argo floats<br/>moored buoys"]
    S3["Copernicus<br/>currents, biology"]
    S4["Your own<br/>NetCDF file"]

    S1 --> AD
    S2 --> AD
    S3 --> AD
    S4 --> AD

    AD["<b>ADAPTERS</b><br/>one per source"]
    AD --> QC["<b>QUALITY CONTROL</b><br/>and derived variables"]
    QC --> GRID

    GRID[("<b>THE GRID</b><br/>full precision<br/>every number comes from here")]

    GRID ==> BROWSER["<b>BROWSER</b><br/>3D ocean, works offline"]
    GRID ==> API["<b>REST API</b>"]
    GRID ==> STD["<b>OPEN STANDARDS</b><br/>OPeNDAP · CF · WMS"]

    GRID -. "compressed copy,<br/>for drawing only" .-> VOL["GPU volume"]
    VOL -. "pixels, never numbers" .-> BROWSER

    classDef src fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e
    classDef work fill:#f1f5f9,stroke:#64748b,color:#1e293b
    classDef out fill:#0891b2,stroke:#0e7490,color:#ffffff
    classDef truth fill:#0f766e,stroke:#115e59,color:#ffffff
    classDef ghost fill:#ffffff,stroke:#94a3b8,color:#64748b,stroke-dasharray:4 4

    class S1,S2,S3,S4 src
    class AD,QC work
    class GRID truth
    class BROWSER,API,STD out
    class VOL ghost
```

**The thick arrows carry numbers. The dotted ones carry pixels.** The compressed copy exists only
so the ocean can be drawn at sixty frames a second, and nothing ever reads a value back out of
it - not the figure under your cursor, not the comparison chart, not a file served to another
program. That one rule is why a number on this platform can be trusted.

**Adding a source touches nothing else.** Each one sits behind a small adapter, and the rest of
the system never learns where data came from. Tested rather than claimed: a later round added
four new providers and changed no renderer, no endpoint and no screen.

## The providers, in full

Each one public, and each tested and dated before it was used.

| Provider | What it gives us |
| --- | --- |
| **INCOIS ERDDAP** `incois_argo_10d_VAM` | The 10-day gridded analysis - temperature and salinity |
| **INCOIS ERDDAP** 10-day McCreary | The second analysis, for the spread between them |
| **Argo GDAC** · Ifremer | Float profiles, with per-channel quality flags |
| **Argo BGC** · Ifremer | Chlorophyll on 57 of the floats and oxygen on 40 |
| **NOAA OSMC** | Moored buoys over GTS - a separate network from the floats |
| **Copernicus Marine** | Current vectors `uo`, `vo` at 1/12° |
| **Copernicus Marine** biogeochemistry | Chlorophyll and dissolved oxygen at 0.25°, and the oxygen floor |
| **Copernicus Marine** satellite | OSTIA sea surface temperature and gap-free chlorophyll, for surface fronts |
| **EGO glider GDAC** · `ftp.ifremer.fr` | The glider archive PS 26067 names |
| **World Ocean Atlas 2023** · NOAA NCEI | The 1991-2020 climatological normal |
| **Your own NetCDF file**, dropped on the page | The eleventh adapter, `POST /api/netcdf` |

---

## Tech stack

| Layer | What | Why this one |
| --- | --- | --- |
| **Science** | Python 3.10+, NumPy, xarray, netCDF4, gsw (TEOS-10) | `gsw` is the international standard for seawater density, so our derived variable is the one an oceanographer would compute. |
| **Colour** | cmocean | Perceptually uniform, and each scale is designed for a specific ocean quantity. A rainbow palette invents boundaries that are not in the data. |
| **Data access** | ERDDAP / OPeNDAP over `requests`, `pydap` | INCOIS and Argo both publish ERDDAP, so no scraping and no private endpoint. |
| **API** | FastAPI + `uvicorn` | Serves the queries a static bundle cannot precompute, and the three open standards below. |
| **Standards out** | OPeNDAP (DAP2), CF-1.8 NetCDF, OGC WMS 1.3.0 | So the analysis is readable by a Python client, a file, or a GIS - not only by this page. |
| **Rendering** | Three.js on WebGL2, GLSL ray marching | The volume is a single ray-marched block, not a stack of images. Nothing else gets you inside the water. |
| **Frontend** | React 18, TypeScript 5, Zustand, Vite | Zustand because every control is one flat store the scene reads once a frame; Vite for a four-page build with no config. |
| **Verification** | pytest, Playwright | 511 tests on the science; 16 Playwright probes that **measure the rendered page**. |
| **Fonts** | Chivo, IBM Plex Mono, Space Grotesk, Inter - all self-hosted | The demo makes zero network calls. A Google Fonts link would be a build failure, not a style choice. |

---

## Run it

**Prerequisites:** Python **3.10+**, Node **18+**, and a browser with WebGL2 (any current one).
No account, no API key, no database.

```bash
git clone https://github.com/RAK2315/oceanverity && cd oceanverity

# 1. install
python -m venv .venv
.venv/Scripts/pip install -r pipeline/requirements.txt      # Windows
# .venv/bin/pip install -r pipeline/requirements.txt        # macOS / Linux
cd web && npm install && cd ..

# 2. run the website
cd web && npm run dev                                       # http://localhost:5173
```

**That is the whole setup.** The baked data is committed, so the platform runs offline from a
fresh clone. The two steps below are optional.

```bash
# optional: the REST API and the three open standards
.venv/Scripts/python -m uvicorn api.main:app --port 8000    # /docs for the OpenAPI page

# optional: rebuild the data from source (a few minutes; needs one free Copernicus account
# for the current velocities, and nothing else)
cd pipeline && ../.venv/Scripts/python -m oceanverity.bake
```

### Check the claims yourself

Nothing in this README is asserted without something that can fail.

```bash
cd pipeline && ../.venv/Scripts/python -m pytest -q    # 511 tests on the science
cd web && npm run typecheck && npx vite build          # the whole front end
```

On top of those, **16 automated browser checks measure what the page actually drew** rather than
trusting that it drew it: every control is explained, every figure on screen came from the data,
the colourbar and the water agree, and the drift model matches the one it was scored against.
They run against a preview server, and two of them also need the API.

---

## Data credits

Argo data are collected and made freely available by the International Argo Program and the
national programmes that contribute to it. The Argo Program is part of the Global Ocean Observing
System. Gridded analysis products are produced by the **Indian National Centre for Ocean
Information Services (INCOIS)**, Ministry of Earth Sciences, Government of India. Cyclone track
data are **India Meteorological Department**, RSMC New Delhi. Current velocity, biogeochemistry
and satellite fields are **E.U. Copernicus Marine Service Information**. Climatology is **NOAA
World Ocean Atlas 2023**. Moored buoy observations via **NOAA OSMC**. Colour scales are
**cmocean** (Thyng et al., 2016). Coastlines are **Natural Earth**.
