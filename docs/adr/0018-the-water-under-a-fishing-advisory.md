# The water under a fishing advisory: chlorophyll, oxygen, the oxygen floor and surface fronts

Decided 2026-09-15, from the research in `docs/research/2026-09-15-integrations-and-datasets.md` and
the owner's decisions in `docs/plan/06`.

## The gap

PS 26067 names fishery advisories among the operational uses of a 3D platform, and the build
answered nothing about them. INCOIS issue Potential Fishing Zone advisories daily from satellite
sea surface temperature and chlorophyll. Their own staff name the limits (iScience 29(7):116421,
2026): clouds in the monsoon, and no easy way to check the advice. A satellite sees the top metre
on a clear day. Nothing INCOIS publish shows the water under the line.

## What was built

A new Field Group, **Biology**, with four Fields.

| Field | Render kind | Source | Checked against |
| --- | --- | --- | --- |
| Chlorophyll | volume | Copernicus `GLOBAL_ANALYSISFORECAST_BGC_001_028`, `chl` | BGC-Argo fluorometers |
| Dissolved Oxygen | volume | the same product, `o2` | BGC-Argo optodes |
| Oxygen Floor | depth (Sheet) | computed here: first depth below 2 mg/L | the oxygen it is cut from |
| Surface Fronts | column (Drape) | computed here from OSTIA SST and GlobColour gap-free chlorophyll | nothing: a method, stated |

Three adapters: `sources/copernicus_bgc.py`, `sources/copernicus_satellite.py`, and the BGC-Argo
layout gaining an oxygen channel. One new module each for the science: `habitat.py` and
`fronts.py`. The render kinds are ADR 0014's; nothing in the renderer changed.

## Decisions worth recording

**Fronts, never fishing zones.** No free archive of past PFZ lines exists for this window (checked
2026-09-15), so the advisory itself cannot be drawn. The ingredient can: thermal fronts by Cayula and
Cornillon (1992) and chlorophyll fronts by Canny, the methods INCOIS name. The Field is labelled as
the ingredient, and a test fails if any Biology Field's label or description calls itself a fishing
zone.

**A share, not a line.** A front is a few kilometres wide and a platform cell about 110 km. The
Field is the percent of each cell's ocean pixels on a front of either kind. Drawing lines finer than
every other number the platform reports would break the rule ADR 0017 set for the current dots.

**Nearest node, as for currents.** The 0.25 degree model lands on the 1 degree grid by nearest
source node, not a box mean, for the reason ADR 0013 gives: a float is compared against a point.

**Oxygen is converted with the float's own density.** Floats report micromoles per kilogram, the
model millimoles per cubic metre. The conversion uses TEOS-10 in-situ density from the cast's own
temperature and salinity, and refuses a level without both rather than assuming 1025 kg/m3.

**A BGC comparison is ranked where the BGC cast was.** The synthetic BGC product often runs one
cycle behind the core cast. Each chlorophyll and oxygen series carries its own time, position and
analysis step, and the bias map uses them.

**Masked to INCOIS's coastline.** Copernicus's land mask is not INCOIS's; values over cells INCOIS
call land are Mask, so the block has one coastline.

**The multi-year ocean-colour product, not the near-real-time one.** The research note said the
NRT gap-free product ran from 2023-10-01. Read on 2026-09-15 it kept nineteen days. The MY product
`OCEANCOLOUR_GLO_BGC_L4_MY_009_104` runs 1997-09-04 to 2026-09-07 and covers the window.

## Limits, said on the panels

- Both biogeochemical Fields are a model. The July 2026 feasibility check found oxygen too high at
  100-150 m and chlorophyll about twice the floats' in the top 100 m; the bias map publishes the
  bake's own figures.
- The oxygen floor inherits the Levels' spacing, 25 m near 100 m.
- Fronts are read on each analysis date only, from gap-free fields that interpolate under cloud.
- The thresholds for fronts are ours for the minimum contrast and the Canny hysteresis; the window
  criterion and cohesion are the paper's.

## Not built

The daily PFZ harvester (a later window), INCOIS HF radar and OMNI currents (a data request the
owner decided not to make), and nitrate (27 floats, no Field to hold it against).
