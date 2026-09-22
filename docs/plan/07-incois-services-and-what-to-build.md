# INCOIS's own service catalogue, and what is worth building before 30 September

**Written 2026-09-21. This is a discussion document, not a decision.** Nothing here is agreed and
nothing here is started.

**Decided later the same day, after checking it against the build.** Two of this file's
assumptions did not hold and are corrected in section 6 at the foot. What was built instead was
`docs/BUGS.md` item 104 - the seven layers WMS, OPeNDAP and CF advertised and could not draw -
which needs no bake, moves no published figure, and was the only candidate whose outcome was
knowable in advance. Nothing from section 3 was built.

**Source and its limit:** the catalogue below was read off screenshots of `incois.gov.in` that
the owner captured on 2026-09-21. **It has not been re-verified against the live site**, no
endpoint behind any of these services has been tested, and the data-access question - open,
registered or on request - is **unknown for every row** unless
[`00-data-sources-verified.md`](00-data-sources-verified.md) already covers it. Anyone acting on
this file checks the service and its access terms first. Several INCOIS holdings are
view-only with no download; see `docs/plan/06` section 1.

---

## 1. What INCOIS actually runs

**Ecosystem Services**
Algal Bloom Information Service &middot; Potential Fishing Zone (PFZ) &middot; Coral Bleaching
Alert System

**Multi-Hazard Services**
Tsunami Early Warning &middot; Storm Surge Warning &middot; High Wave Alerts &middot; Oil Spill
Advisory &middot; INCOIS-IMD Joint Bulletin &middot; Small Vessel Advisory Service (SVAS) &middot;
**Search and Rescue Aid Tool (SARAT)** &middot; **Marine Heatwave Advisory Services (MAHAS)**
&middot; Swell-surge Inundation Vulnerability Advisory System (SIVAS)

**Forecast / Nowcast Services**
Ocean State Forecast &middot; Predicted Astronomical Tide &middot; Ports and Harbours &middot;
Forecast along ship routes &middot; Water Quality Nowcast System &middot; **Tropical Cyclone Heat
Potential** &middot; Location Specific Forecasts &middot; Global Forecast &middot; Ocean Energy
Atlas

**Also listed:** Climate Services, International Services, Ocean Observations (Argo floats,
tsunami buoys, gliders, moored buoys, tide gauges, HF radar, drifting buoys, ships), the Deep
Ocean Mission, and ICT and Engineering Services.

---

## 2. The finding that matters for the deck

**INCOIS runs roughly twenty operational services and almost all of them stand on the same two
things this platform already holds: a gridded model field, and the in-situ instruments in the
same water.** OceanVerity is not a twenty-first service competing with those. It is the common
3D substrate underneath a good number of them.

That is a positioning line, and it is checkable, which is the kind this deck wants. It also
sharpens what "no new mandate" on slide 5 means: **every job the deck claims is one of the
services above**, by name.

Three of their services already have a direct counterpart in the build:

| INCOIS service | What this platform already does |
| --- | --- |
| **Tropical Cyclone Heat Potential** | Computed from INCOIS's own Argo analysis and checked against INCOIS's own published values, same number in **97.2%** of cells (`ppt/FACTS.md`) |
| **Search and Rescue Aid Tool (SARAT)** | The drift model, and the only one of the two with its error published. Worth naming SARAT explicitly on a slide |
| **Potential Fishing Zone** | The *ingredients* - surface fronts, chlorophyll, oxygen, the oxygen floor - deliberately never called a fishing zone. ADR 0018 |

---

## 3. Candidates, with the honest cost of each

**Nothing below is agreed.** They are ordered by what they would buy the submission against what
they would cost, and every one of them needs a **36-step bake, about 36 minutes**, which clears
`volumes/`, `currents/`, `surfaces/`, `grids/` and `data/grids/*.npz` before writing.

### A. Marine heatwaves, below the surface

**The single strongest candidate, and it is already half-planned** - `docs/plan/06` section 6
item 7. INCOIS's MAHAS is built on sea surface temperature. This platform holds the whole column
and a real 1991-2020 baseline (ADR 0016), so *"a marine heatwave, and how deep it goes"* is a
question their own service cannot answer and this one nearly can.

**Cost:** a derived Field with a threshold (the literature uses the 90th percentile of a
climatology), a guide entry, a tour step, a bake. **Risk:** the honest definition needs a daily
climatology and we have a monthly one, so the threshold has to be defensible or the Field is a
plausible wrong number, which this project has a rule against.

### B. Naming SARAT and TCHP on the deck

**Zero build.** Slide 5 already claims search and rescue and cyclone hazard. Naming INCOIS's own
service beside each turns a generic claim into one a judge can check in a browser tab.
**Do this whatever else happens.**

### C. Coral bleaching

Degree Heating Weeks from satellite SST, which the Copernicus satellite adapter already reads.
**Cost:** a derived Field and a bake. **Risk:** DHW is conventionally computed against a
specific climatology product; using the wrong one gives a finite, believable, wrong number.

### D. Algal blooms

Chlorophyll is already a Field. A bloom indicator is a threshold on it. **Cheap, and the weakest
of the four** - it adds a label to something already on screen rather than a capability.

### E. Wind and waves in drift

`docs/plan/06` item 7. It would make the drift model closer to a real search-and-rescue tool and
**it would change the published drift score**, which the deck and the video both quote.

---

## 4. The argument against building any of it

Nine days, as of 2026-09-21. The deck, the screenshots and the video are all outstanding, and
**every option above needs a bake, which invalidates screenshots taken before it**. The owner's
own recorded decision on item 7 was to defer it for exactly that reason.

**The submission is judged on the deck, not on the feature count.** A feature added on 27
September that nothing on the deck mentions has bought nothing; a feature that changes a figure
the deck quotes has cost something. If anything is built, the order has to be: build, bake,
re-run `collect_facts.py` and `check_figures.py`, re-take screenshots, then update the deck and
the video.

**Option B costs nothing and is the only one I would take without discussion.**

---

## 5. The other open documents, for a session picking this up

| File | What is still open in it |
| --- | --- |
| [`06-fixes-from-2026-09-15-research.md`](06-fixes-from-2026-09-15-research.md) | **Section 6, item 7**: the PFZ harvester, marine heatwaves, a forecast scorecard, wind and waves in drift. Items 1 to 6 are done and pushed. Section 5's README video line may still be open. |
| [`05-coverage-audit-and-ideas.md`](05-coverage-audit-and-ideas.md) | The PS audited clause by clause, and a ranked idea list with costs. **Partly out of date**: it says fishery advisories is the one unanswered mandate, and ADR 0018 answered it on 2026-09-15. |
| [`03-requirement-gaps.md`](03-requirement-gaps.md) | Every unmet PS clause, researched with dates and row counts, and the decision taken on each. **Read this before proposing any new data source.** |
| [`01-cut-features.md`](01-cut-features.md) | What was cut, what is worth adding back, and the known rough edges. |
| [`02-next-features.md`](02-next-features.md) | The older feature list. The bias map came from here and is built. |
| [`../BUGS.md`](../BUGS.md) | The public defect list. |
| [`00-data-sources-verified.md`](00-data-sources-verified.md) | Every endpoint tested, **including the dead ones**. Check here before assuming an INCOIS service is reachable. |

---

## 6. What was checked against the build, 2026-09-21, and what it changed

Everything below was read off the build or a live endpoint on 21 September. Section 4's argument
rests on two claims and neither survived.

**"Every candidate needs a bake, and a bake moves every figure." A bake would re-cut the same
window.** INCOIS's ERDDAP time axis holds 813 analyses, newest 2026-07-30, which is exactly the
last Timestep the shipped manifest carries. `bake.py` takes `list(model.timesteps())[-timesteps:]`
and anchors the Argo fetch to that same end date, so the grid side would not move at all. What
could still move is Argo-derived - float counts have churned upstream before - and the Copernicus
products were not re-checked.

**"A bake invalidates screenshots." They are already invalid, for two other reasons.** The
committed set is dated 4 September, which is before the 15 September biology bake and before the
rename. `assets/screenshots/light/volume.jpg` shows four Variable tabs where there are now six
groups, no Biology, no Hazard mode, and the all-caps mono labels the chrome restyle retired. Bare
frames with no chrome, like `dark/hero.jpg`, survive both. The re-capture is owed whatever is
built.

**Item 134 was already closed and this file's section 5 pointed at it as open.** The 15 September
bake ran the plausibility mask: the manifest carries `masked` with 25 temperature cells, and the
maximum across all 144 shipped temperature Grids is 34.40 degC.

**Item 104 had grown from five layers of fourteen to seven of eighteen**, because `oxygen_floor`
and `fronts` are surfaces too. Fixed the same day by serving them rather than refusing them;
`docs/BUGS.md` has the measurements.

### On candidate A, and why it stays refused

Marine heatwaves need a percentile of a daily climatology. `data/woa/*.npz` carries `values` and
nothing else - no standard deviation, no percentile - so the threshold would have to be invented,
which is the rule ADR 0010 exists for. Candidate C fails the same way.

### On candidate E, and the order it was written in

The wave data is real: `cmems_mod_glo_wav_anfc_0.083deg_PT3H-i` opened with the credentials on
this machine carries `VSDX`, `VSDY` and `VHM0`, 3-hourly, 11,440 steps from 2022-11-01 to
2026-10-01, covering the whole window.

**But this file's reason for deferring it is wrong.** Stokes drift is a surface quantity and
`drift.py` scores at `PARKING_DEPTH_METRES = 1000.0`, so scoped to the surface it cannot move the
41 km figure the deck and the video quote.

**And the order is backwards.** Adding wind and waves before a surface score gives physics nobody
can check. The score first, then the physics as a measured improvement. A surface score looked
cheap: NOAA's OSMC lists **54 drifting buoys and 101,100 position fixes** over the exact window,
36 tracks longer than 30 days and 25 longer than 90, open and no login, from the ERDDAP server
`osmc.py` already reads - that adapter filters to `MOORED` on purpose and the drifters were always
in the same table. And it would need no bake, because `currents/vectors_*.bin` holds u and v at 24
levels on the Grid for all 36 steps and `refresh_anomaly_spread.py` is the precedent for writing
into the shipped manifest without one.

**What blocks it is drogue status.** An undrogued drifter slips with the wind at one to two
percent of wind speed, which is exactly the physics a current-only model does not have, so pooling
them puts wind slip inside a number labelled *how wrong the current field is*. The Global Drifter
Program's QC'd products are the only open source for `drogue_lost_date` and both stop before the
window opens: the hourly one ends 2022-10-31, the 6-hourly ends 2025-06-18, and the window opens
2025-08-10. Checked against the ten largest tracks: seven are in the archive, one (WMO 4101867)
lost its drogue on 2024-07-01 and is undrogued throughout, six come back blank - which against an
archive ending in June 2025 means unknown rather than attached - and three are not there at all.

Two further limits even with drogue status solved: the surface score will probably be worse than
41 km and cannot be un-measured once shipped, and Copernicus surface current is a daily mean at
the top level while a drogued drifter sits at 15 m, so that shear belongs in the caveat rather
than in the error.

**Not re-checked:** whether another source resolves the nine unknown drifters, whether the
Copernicus currents, BGC and satellite products have moved since 15 September, whether Ifremer's
Argo archive has changed for this window, and this file's own catalogue against the live site.
