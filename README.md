<div align="center">

# Samudra 3D

**Fly into the Indian Ocean and see, in one picture, what the model predicted
and what the instruments in the water actually measured.**

[![Launch the platform](https://img.shields.io/badge/Launch-the%20platform-0f766e?style=for-the-badge&logo=googleearth&logoColor=white)](https://rak2315.github.io/samudra-sih26/app.html)
[![Landing page](https://img.shields.io/badge/Landing-page-0891b2?style=for-the-badge)](https://rak2315.github.io/samudra-sih26/)
[![Provenance](https://img.shields.io/badge/Every%20figure-sourced-155e75?style=for-the-badge)](https://rak2315.github.io/samudra-sih26/provenance.html)

Smart India Hackathon 2026 &middot; Problem Statement **26067** &middot; MoES / INCOIS
&middot; Software &middot; Disaster Management &middot; Team Sigmoid

![Tests](https://img.shields.io/badge/tests-377%20passing-2ea043)
![Probes](https://img.shields.io/badge/browser%20probes-13%20green-2ea043)
![Network calls at demo time](https://img.shields.io/badge/network%20calls%20at%20demo%20time-0-2ea043)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Three.js](https://img.shields.io/badge/three.js-WebGL2-000000?logo=threedotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST-009688?logo=fastapi&logoColor=white)

<img src="docs/images/collocation.jpg" width="880" alt="The platform running: a three-dimensional block of Indian Ocean water from 5 m to 2000 m with Argo float markers across the top, the control panel on the left, and on the right a chart plotting one float's measured temperature against the model's down the same depth axis.">

*One frame, and the whole argument. INCOIS's 30 July 2026 analysis as a block of water you fly
into, the floats drawn where they actually were, and one float's cast scored against the model:
**54 depths compared, 0.08 °C average gap, "moderate disagreement"**.*

</div>

---

## The problem

India runs an ocean model. India also has robot floats drifting in that same water taking real
measurements. **You cannot currently look at the two together.** The model lives in one desktop
program, the measurements in another, and both draw flat maps one depth at a time. So the
question a forecaster actually has - *is the model right, here, at this depth, today?* - has no
tool behind it.

PS 26067 asks for a 3D visualisation of INCOIS's ocean data. We read that as: **the picture is
not the deliverable. The comparison is.**

## What we built

A website that draws the ocean as a solid block of water you fly inside, from 5 m to 2000 m,
with the instruments sitting in it where they actually were. Click one and it tells you what it
measured against what the model predicted at the same place on the same day, and **puts a number
on how far apart they were** - whichever way that number comes out.

It opens in a browser, needs no account, and **makes zero network calls at demo time.** A dead
venue network cannot kill it.

| | |
| --- | --- |
| **Live** | [Landing page](https://rak2315.github.io/samudra-sih26/) &middot; [The platform](https://rak2315.github.io/samudra-sih26/app.html) |
| **Every figure, sourced** | [provenance.html](https://rak2315.github.io/samudra-sih26/provenance.html) |
| **Every PS clause, answered** | [requirements.html](https://rak2315.github.io/samudra-sih26/requirements.html) - each clause links straight to the control that answers it |

---

## What makes it different

**1. It publishes its own error.** Most visualisations show you the model and stop. This one
scores the model against every instrument in the water and prints the result, including where it
looks bad.

> Across **230 instruments** the typical gap is **0.19 °C**. But INCOIS *assimilate* Argo, so a
> float's agreement is largely the model agreeing with itself. Against the **9 moored buoys it
> did not ingest, the gap is 0.75 °C** - four times worse. We print both, separately, because
> pooling them would flatter the model.

**2. Never answer a scientific question from the picture.** The rendered block is quantised to a
byte per value and warped for the GPU. Every number a user reads - tooltips, comparisons, API
responses - comes from the full-precision grid instead. This one rule shapes the whole
architecture.

**3. A gap is drawn as a gap.** Where nobody measured, we say so rather than colouring it in.
**9.9%** of the block has no observation behind it, and there is a variable whose only job is to
show you where.

**4. It has a second door.** Fifteen variables is right for a forecaster and wrong for a school
group, so `Explore` turns the platform into eight plain questions, and `?kiosk=1` runs it
unattended on an exhibition screen.

---

## The numbers

Every figure below is read off the running build by
[`pipeline/scripts/collect_facts.py`](pipeline/scripts/collect_facts.py). Nothing is typed by
hand.

| | |
| --- | --- |
| Instruments in the water | **237** - 228 Argo floats + 9 moored buoys |
| Variables | **15**, in 5 groups; 13 computed or fetched here |
| Analyses | **12** timesteps, 10 Apr to 30 Jul 2026, over 45-100 °E and 10 °S-25 °N |
| Depth | **5 m to 2000 m** across 24 uneven levels |
| Data shipped in the build | **71.1 MB**, committed, **0** network calls to run |
| Source adapters | **9** - 8 providers, plus one for a file a visitor drops on the page |
| Tests / browser probes | **377** / **13** |
| Drift model, scored | median **38.5 km** out over one Argo cycle, across 1,908 cycles on 195 floats |

## What it looks like

| | |
| --- | --- |
| <img src="docs/images/volume.jpg" width="420" alt="The ray-marched volume: the full ocean depth as one solid body of water."> | <img src="docs/images/bias.jpg" width="420" alt="The bias map: every instrument coloured by how far the analysis sat from what it measured."> |
| **The water column.** The whole depth as one body, not a stack of slices. | **Where the model is wrong.** Every instrument coloured by its own disagreement. |
| <img src="docs/images/hazard.jpg" width="420" alt="Cyclone heat potential draped on the sea surface."> | <img src="docs/images/drift.jpg" width="420" alt="A drift track integrated forward through the current field from a dropped pin."> |
| **Cyclone mode.** One press swaps in the five things a cyclone forecaster asks for. | **Drift.** Drop a pin, follow the current. The model publishes its own median error. |
| <img src="docs/images/section.jpg" width="420" alt="A vertical section cut along a drawn line, with float casts overlaid."> | <img src="docs/images/kiosk.jpg" width="420" alt="Kiosk mode on an exhibition screen, type scaled for reading across a room."> |
| **Vertical section.** Draw a line, cut the ocean along it. | **Exhibition mode.** The same platform, for a room full of students. |

*Every picture is the running build. Nothing is a mockup and nothing is retouched.*

---

## Architecture

**It is a fork, not a pipeline.** That is the one thing worth understanding, and it exists to
enforce the rule above.

```
  8 public providers            ┌──────────────────────────────────────────┐
  + a NetCDF file a visitor     │  THE GRID                                │
    drops on the page           │  float64, provider's own axes            │
        │                       │  land is NaN, never zero                 │
        │                       │  ── the scientific truth ──              │
        ▼                       └──────────────────────────────────────────┘
  ┌──────────────┐                    │                    │
  │ SOURCE       │  Grid /            │ numbers,           │ quantise +
  │ ADAPTER SEAM │  Profile           │ unchanged          │ depth-warp
  │  9 classes   │ ─────────►         │                    ▼
  └──────────────┘                    │           ┌─────────────────┐
   one class per provider,            │           │  THE VOLUME     │
   subset at the server,              │           │  1 byte a value │
   QC flags read per channel          │           │  even depth axis│
                                      │           └─────────────────┘
                                      ▼                    │
                         ┌────────────────────────┐        │ pixels only,
                         │ REST API · OPeNDAP     │        │ never a reading
                         │ CF-1.8 NetCDF · WMS    │        ▼
                         │ every panel, tooltip   │   ┌──────────┐
                         │ and comparison         │   │  SCREEN  │
                         └────────────────────────┘   └──────────┘
```

The left half is ordinary: nine adapters read nine formats and hand back one `Grid`. Everything
after that has never heard of ERDDAP or NetCDF.

The right half is the point. From the `Grid`, **numbers** go straight out to the API, the open
standards and every panel in the browser. The `Volume` is a **branch off** the `Grid`, not a
stage in it, and its only arrow goes to the screen. **Nothing reads a number back out of it.**

### Three layers, and what separates them

| Layer | Responsible for | The seam below it |
| --- | --- | --- |
| **`pipeline/`** · Python | Reading every provider, quality-controlling every observation, computing every derived variable, writing the bake. **All tested logic lives here** - 377 tests. | `samudra/sources/base.py`. A provider is one class. Nothing above this file knows a provider exists. |
| **`api/`** · FastAPI | What a static folder cannot answer: an arbitrary column, an arbitrary section line, an uploaded NetCDF file. Also serves OPeNDAP, CF-1.8 NetCDF and OGC WMS. | `data/grids/*.npz`. **Every endpoint reads the `Grid`. None can reach a `Volume`.** |
| **`web/`** · React + TypeScript + Three.js | One WebGL scene for globe and volume, every control and panel, and the two pieces of science that must run offline. | `web/public/data/`. The browser reads **files, not endpoints** - the only exception is a file the user drops. |

They are genuinely separable: the pipeline runs with no browser, the browser runs with no API.
That is not tidiness - it is why the demo survives a dead network, and why the public deployment
works with no server behind it at all.

### The data path

1. **Provider** - eight public endpoints, each tested and dated in
   [`docs/plan/00-data-sources-verified.md`](docs/plan/00-data-sources-verified.md).
2. **Adapter** - one class per provider, subsetting *at the server* so we pull one region and one
   window. Argo's own QC flags are read per channel, then a regional salinity floor catches what
   the global standard lets past. Land is masked, never filled.
3. **Grid** - `time × depth × lat × lon`, float64, on INCOIS's own mesh. **The scientific truth.**
4. **Derived variables** - density, cyclone heat potential, mixed layer depth and ten more,
   each computed here and each held to a hand-computable test.
5. **Bake** - the `Volume` for the GPU, plus float32 grids, float positions, collocations,
   residuals and the drift check. 71.1 MB, committed.
6. **Browser** - reads those files. No network.

---

## Run it

```bash
# 1. install
python -m venv .venv && .venv/Scripts/pip install -r pipeline/requirements.txt
cd web && npm install

# 2. get the data (a few minutes: INCOIS, Argo, BGC-Argo, NOAA buoys, Copernicus, NOAA WOA)
cd pipeline && ../.venv/Scripts/python -m samudra.bake

# 3. run the website
cd web && npm run dev                                      # http://localhost:5173

# 4. optional: the REST API and the open standards
.venv/Scripts/python -m uvicorn api.main:app --port 8000
```

```bash
# tests
cd pipeline && ../.venv/Scripts/python -m pytest -q        # 377 tests
cd web && npm run typecheck && npx vite build
```

The data is committed, so **step 2 is optional** - clone and run.

---

## Where to look

| | |
| --- | --- |
| [`CONTEXT.md`](CONTEXT.md) | Domain vocabulary and the scope cut line. **Read first.** |
| [`docs/adr/`](docs/adr/) | Seventeen decision records, several documenting traps that cost hours. |
| [`docs/README-full.md`](docs/README-full.md) | The long-form version of this file: every clause of the PS answered, every variable explained, the full architecture. |
| [`docs/BUGS.md`](docs/BUGS.md) | A public defect list. 100 fixed, 2 open by design. |
| [`docs/plan/`](docs/plan/) | Every endpoint tested including the dead ones; the requirement gaps and the decision on each. |
| [`ppt/`](ppt/) | The deck, the video script, and every figure they may quote. |

## What we deliberately did not build

Saying no is part of the design.

- **Geostrophic current speed.** Prototyped and rejected: it reported 0.16 m/s for the Somali
  Current against a real 1.5-2.5 m/s. Finite and plausible-looking is not the bar. (ADR 0010)
- **3-D particle advection.** Nobody publishes vertical velocity for this region, so a 3-D
  particle would claim a motion no one measured. The flow is drawn on one level instead. (ADR 0017)
- **A palette chooser.** A palette belongs to a variable, not to a dropdown. (ADR 0010)
- **Login, upload storage, write access.** The platform is read-only. The one endpoint that
  accepts anything holds it in memory and stores nothing.

---

## Data credits

Argo data are collected and made freely available by the International Argo Program and the
national programmes that contribute to it. The Argo Program is part of the Global Ocean Observing
System. Gridded analysis products are produced by the **Indian National Centre for Ocean
Information Services (INCOIS)**, Ministry of Earth Sciences, Government of India. Current
velocity is **E.U. Copernicus Marine Service Information**. Climatology is **NOAA World Ocean
Atlas 2023**. Moored buoy observations via **NOAA OSMC**. Colour scales are **cmocean** (Thyng et
al., 2016). Coastlines are **Natural Earth**.
