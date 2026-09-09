# Every figure the deck may use, read off the build

**Generated 2026-09-09 by `pipeline/scripts/collect_facts.py`. Do not edit by
hand.** Re-run it after a bake and diff this file: a figure that moved shows up as a line.

`ppt/DECK.md` is written by a person and quotes these numbers. This file is the source it quotes
*from*, so "do not adjust a number by arithmetic" has somewhere to point.
Every row names where the figure comes from, so a judge's question can be answered by opening a
file rather than by remembering.

**One figure on the deck is not here, on purpose.** The share of the frame a rendered layer
covers is measured by a probe against a randomly seeded particle population, so it is a range and
not a point - see `CLAUDE.md`.

## The build

| | | Where it comes from |
| --- | --- | --- |
| Fields, selectable | **15** in 5 groups | `manifest.fields` |
| Source Adapters | **9** - 8 providers plus one for a file a visitor drops | `manifest.sources`, plus `sources/netcdf.py` |
| Analyses baked | **36** Timesteps, 10 Aug 2025 to 30 Jul 2026 | `manifest.timesteps` |
| Region | 45-100 E, 10 S-25 N | `manifest.region` |
| Volume lattice | **56 x 36 x 48**, 4 bytes a voxel | `manifest.volume` |
| Depth range | 5 m to 2000 m over 24 uneven levels | `manifest.volume.levelMetres` |
| Static bake | **192.0 MB**, committed, **0** network calls to run | `du web/public/data` |
| HTTP routes on the API | **21** | `api/*.py` |
| Tests | **379** | `web/public/data/tests.json` |
| Browser probes | **15** | the allowlist in `.gitignore` |

## Instruments

| | | Where it comes from |
| --- | --- | --- |
| Instruments in the water | **276** = 259 Argo floats + 17 moored buoys | `manifest.instruments` |
| Carrying chlorophyll | **57** floats | `manifest.instruments.withChlorophyll` |
| Drawn at any one Timestep | between 192 and 220 floats and 5 to 9 buoys | `reportingByKind()`, measured across the twelve steps |

## How far the model sits from the instruments

| | | Where it comes from |
| --- | --- | --- |
| Compared | **266** instruments | `residuals.fields.temperature.summary` |
| Typical gap, all instruments | **0.24 degC** | `summary.meanAbsBias` |
| Typical gap, Argo floats | **0.18 degC** across 249 | `byKind.float` |
| Typical gap, moored buoys | **1.01 degC** across 17 | `byKind.mooring` |
| Worst instrument | **23094** (mooring), model warmer by 3.22 degC over 7 depths | `residuals` ranked on `scaledRms` |

## Drift, and its score

| | | Where it comes from |
| --- | --- | --- |
| Scored on | **219** Argo floats at **1000 m** | `manifest.drift` |
| Over one Argo cycle | median **40.9 km** out, p90 92.7 km, across **6,246** cycles | `manifest.drift.cycle` |
| Over 10 days | median **43.2 km** out on 214 floats, against 44.5 km travelled | `manifest.drift.horizons` |
| Over 30 days | median **105.0 km** out on 206 floats, against 108.1 km travelled | `manifest.drift.horizons` |
| Over 60 days | median **166.0 km** out on 205 floats, against 143.8 km travelled | `manifest.drift.horizons` |
| Over 90 days | median **211.9 km** out on 198 floats, against 164.8 km travelled | `manifest.drift.horizons` |

## Evidence and change

| | | Where it comes from |
| --- | --- | --- |
| Block with no cast behind it | **10.2%** | `manifest.coverage.emptyFraction` |
| Coverage radius | casts within **334 km** and 5 days either side of the analysis | `manifest.coverage` |
| Anomaly features found | **404** bodies of water across 36 analyses | `anomalies.json` |
| A feature is marked only past | **0.5 degC** and 2.0 standard deviations | `manifest.anomalyFeatures` |
| Against the 1991-2020 normal | across **1,049,076** cells: mean +0.07 degC, 95th percentile of the magnitude 2.05 degC | `manifest.normalAnomaly` |

## The glider finding

| | | Where it comes from |
| --- | --- | --- |
| Archive read | `ftp.ifremer.fr/ifremer/glider/v2` | the archive PS 26067 names |
| Casts in this box | **2,876** from 1 glider, 2 deployments | `manifest.gliders` |
| Newest cast | **14 Oct 2022**, and nothing since | `manifest.gliders.newestCast` |
| Casts inside this build's window | **0** | which is why none are drawn |

