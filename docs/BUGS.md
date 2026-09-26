# Known defects and open suspicions

**One item is open. Everything else is in the summary table at the foot, and the detail is
in `CLAUDE.md`, an ADR, a probe or a test.** Count the `- [ ]` markers before trusting that
sentence; the header has been wrong before, once saying "three open" over two.

Rewritten on **2026-09-23**. It had reached 138 numbered items, 136 of them closed, and 36 of
those still carried a full paragraph under a heading that said `## Still open` - which is the
file's own convention broken by the file itself:

> The fixed ones are summarised rather than listed. A defect whose measurement has been folded
> into `CLAUDE.md`, an ADR or a probe does not need a paragraph here, and a file that is 90%
> solved problems is a file nobody opens to find the ones that are not.

Nothing was deleted that was not already recorded somewhere a reader would find it. Where a
closed item was the only home for a measurement, that measurement moved before the item did.

**The ranking, unchanged:**

1. **Tells a user something false.** A wrong sentence on screen costs more than a missing feature.
2. **Data quietly discarded, or quietly invented.** Silence about what was dropped, or about what
   was assumed, is the same fault one level down.
3. **Labels, presentation and performance.** Cheap to fix, and "cosmetic" is worth measuring
   before believing.

---

## Open

- [ ] **44. Nothing checks that a caption still describes its picture.**
      Every landing-page and README picture carries prose beside it, and some of it names
      colours. A theme change, a re-capture or a differently chosen frame makes that false and
      nothing notices. `probe-landing.mjs` checks a picture *exists*, *loads* and *follows the
      theme*; it cannot check that the sentence under it is true.

      **This stays open on purpose**: it is a judgement about prose, and a probe that guessed at
      it would be worse than none.

      The mitigation, from the two instances that were found and fixed: **describe the role, not
      the colour.** *"Green is the instrument, dashed blue is the model"* was in four documents
      while `styles.css` painted the observed curve teal and the model curve grey; all four say
      *solid line*, *dashed line* and *the band between them* now, which is true in both themes
      and survives a re-capture. **A caption that names a colour has a shelf life.**

      Related and still true: **every committed screenshot is stale.** The set is dated
      4 September, before the 15 September biology bake (19 Fields, not the 14 in the frames) and
      before the 20 September rename. A re-capture is owed.

---

## Fixed on 2026-09-24: four defects from the owner's own walkthrough

**Found by driving the running app, not by a probe**, which is why all four are interaction or
placement defects rather than wrong numbers - the probes measure what is drawn and none of them
had ever put two guided flows on screen at once or dragged the map key. Each was reproduced in a
browser and measured before anything was edited, and each is now checked by a probe that was
**made to fail on purpose first** against a build with the fix taken back out.

- [x] **139. The right bay's fold tab floats beside the globe cue card and reads as its close
      button.** Nothing is mounted in the right bay until the reader touches a control, so on the
      globe the tab docked to an edge that was not there. Measured at 1400x800: the cue card
      *India's Exclusive Economic Zone* was 320x149 at 1062,88 and the tab was a 22x34 square at
      1030,61 - detached, 32 px off the card's left edge and 27 px above its top, with
      `.panel-right` absent from the document.

      **The misreading is confirmed rather than corrected**: pressing it does hide that card,
      because the fold rule covers `.cue` as well, and the tab then jumps to the frame edge at
      1378. So a reader gets a close button that also folds a bay they cannot see.

      Closed by `useBayFilled` in `web/src/ui/BayToggle.tsx`: a tab is drawn only where its bay
      holds a panel. **Presence, not width** - a folded panel is `display: none` and measures
      zero, and that is exactly the state the tab exists to undo, so the standing
      `getBoundingClientRect()` rule is read the other way round here. Verified after: absent on
      the globe, present the moment `.panel-right` mounts at 1052,51 with the tab docked exactly
      to its left edge at 1030, and still present while the bay is folded. `probe-chrome.mjs`
      checks both sides in both themes and went red on the pre-fix build.

- [x] **140. Starting the tour on top of the Montha walkthrough left both cards and the storm
      track on screen.** `tourStep` and `caseStep` are independent, both draw a card at the foot
      of the screen, and nothing made them exclusive. Measured after Explore, Cyclone Montha,
      then *Show me around*: `tourStep=0` and `caseStep=0`, two `aside.tour` cards at 700,474 and
      700,495 - **21 px apart**, the second reading out from behind the first.

      **Six places opened a flow and only three of them closed the other.** The two Explore
      walkthrough cards and an Explore question cleared `tourStep`; the top bar's *Show me
      around*, Explore's *Show me every control instead* and the `?tour=1` deep link each wrote
      the field directly and cleared nothing.

      **The track was the owner's question and the decision is that it goes.** It is drawn only
      while `caseStep` is a Montha step, and `MapKey` names it in the legend under exactly the
      same condition - so a track that outlived its walkthrough would be an unnamed mark on the
      water, which this project's own rule forbids. The 23-step tour explains no storm track
      either. Ending the walkthrough therefore takes its track with it, which is what the card
      fix does anyway.

      Closed by `startTour()` and `startWalkthrough()` in `web/src/store.ts` - one rule, in one
      place, and all six openers plus the deep link go through them. `probe-tour.mjs` presses the
      real buttons both ways round and follows `?tour=1&case=montha`, and went red on the pre-fix
      build.

      **One sibling hole was closed with it**, in `explore.ts`'s own `calm()`: it cleared
      `tourStep` and not `caseStep`, and the exhibition loop calls a question's `run` directly
      rather than through `Explore.tsx`, which does clear both. `?kiosk=1&case=montha` would have
      left a walkthrough card over every question the screen played.

- [x] **141. "Mark them in the water" was off by default in Anomaly Features after anything that
      touched cyclone mode.** `hazardPreset()` - which *Set up a cyclone question* and several
      Explore questions call - set `showAnomalies: false`, and `selectField` never reset it.
      Measured: selecting the anomaly Field from a fresh session gives a ticked checkbox and
      `showAnomalies: true`; running `hazardPreset()` and selecting it again gives an **unticked**
      checkbox and `false`, with nothing on screen saying why.

      It is the standing *hiding a control is not turning it off* rule, one field along. The rings
      are drawn on the anomaly Field alone, so `hazardPreset`'s line did nothing on the Field it
      was written for and everything on the next Field the reader chose - a state set where no
      control exists, taking effect where one does.

      Closed in `web/src/store.ts`: `selectField` resets `showAnomalies` like every other render
      hint, and `hazardPreset` no longer sets it at all. `cases.ts`'s `calm()` dropped it too -
      every walkthrough step selects a Field immediately afterwards, so it could never take
      effect there, and `Tour.tsx`'s `calm()` had never set it. `probe-controls.mjs` checks the
      checkbox after the preset.

- [x] **142. The depth ruler's caption followed the map key around the screen.** The caption reads
      the key's bounding box every frame to find a floor it must stay above, which is right for
      the time axis - a fixed band on the foot of the frame - and wrong for a legend the reader
      can drag anywhere. Only the top edge was read, so the key raised the floor wherever it went.

      Measured at 1400x800 in the volume view: the key at y 570 and the caption at y 547;
      dragging the key to y 214 took the caption to **y 215**; parking the key in the top right
      corner at 960,42, clear of the caption's column with nothing to avoid at all, still pulled
      the caption to **y 30**. `probe-chrome.mjs` measures the same thing at 1366x768 and read
      493 to 73 and 493 to 62 on the pre-fix build, in both themes.

      Closed in `web/src/ui/DepthRuler.tsx`: a band is in the way only where it overlaps the
      caption's own column **and** reaches down to where the caption is going, and the bands are
      folded lowest-first so that clearing the time axis cannot walk the caption into a key
      parked just above it. Verified after: the caption holds 356,724 at 1400x800 and 356,692 at
      1366x768 through three drags, including one into its own column.

      **One thing did not change and is worth writing down.** Where the column's foot runs past
      the time axis the caption has to be pushed up into the figures, and it overlaps one of
      them. Before the fix it overlapped *300 m* by 14 px of box; it now overlaps *2000 m* by 8
      px. Same squeeze, smaller overlap, and at the foot of the column where the caption belongs
      rather than in the middle of it.

---

## Fixed, in summary

**132 defects across the six rounds to 2026-09-11, 26 more in the audit round, and the four above.**
Item numbers ran to 142 and three are open, which are the three under `## Open`. Every measurement worth keeping is in
one of four places, which is why they are not repeated here: a rule in `CLAUDE.md`, a decision
record in `docs/adr/`, a probe that fails if it comes back, or a test.

The row count and the item count do not reconcile exactly, and never have: the six earlier rounds
below sum to 132 while the numbering reached 138, because a few items were filed outside a round.
The previous version of this line said "132 defects across **five** rounds" over a table of six.

| Round | What it was | Where the detail lives |
| --- | --- | --- |
| **2026-09-03**, 51 items | The September survey. The bias map pooling floats with buoys; the drift score measured on days the current field does not cover; casts drawn on a section they were not in; a corridor measured against a rhumb line where the drawn line is a great circle; a masked corner refusing a whole column; render hints leaking between Fields; the log scale offered where it means nothing | ADRs 0015-0017, and the rules block in `CLAUDE.md` |
| **2026-09-04**, first pass, 12 items | The isosurface sharing the haze's coverage floor and putting sheets over India; current trails coloured by the value they sit on; a capture borrowing kiosk mode; volume controls hidden on a Field that draws a volume; `getBoundingClientRect()` on a hidden panel returning zeros | New rules in `CLAUDE.md`; `probe-hazard.mjs`, `probe-guide.mjs`, `probe-bias.mjs` |
| **2026-09-04**, second pass, 8 items | Two landing cards with alt text over an empty panel; a hero unreadable on light at 1.27:1; five hazard variables that all opened the same way; a heading claiming sixteen cards over fourteen | `probe-landing.mjs`, and three more rules in `CLAUDE.md` |
| **2026-09-04**, third pass, 8 items | Four folders holding overlapping copies of the same pictures; a publish silently replacing thirteen dark images with light ones; pictures that did not follow the theme toggle; `probe-upload.mjs` unable to run from a clone | `assets/screenshots/` as the single source; `collect_facts.py` and `ppt/FACTS.md` |
| **2026-09-04**, fourth pass, 21 items | **The prose sweep.** `provenance.html` printing a superseded line with `undefined m` in it; two requirements links labelled *Open a float comparison* that started the guided tour; a landing tile pairing a median RMS with a mean absolute bias under a caption saying they were one distribution; `longitude = 46` hardcoded on the page whose banner says nothing is; **four of the thirteen probes that could not go red** | `CLAUDE.md`'s Commands block, the four probes' own assertions |
| **2026-09-11**, 32 items | **A read-only sweep of every surface**, and six suspicions measured. Copernicus current speed attributed to INCOIS over WMS and the five hazard Fields captioned as somebody else's; ten Fields served over CF as dimensionless; a guide bullet quoting a spread from a bake that is gone; ADR 0016 with the sign of its mean backwards; a `--timesteps` default that would have replaced the committed bake with a third of it; decibars in a depth axis | `test_standards.py`, `spread_by_level` and its tests, `test_copernicus.py`, `probe-guide.mjs`'s count, the two `refresh_*` scripts |
| **2026-09-21 to 24**, 26 items | **The whole-project audit**, `audit/2026-09-22-audit.md`. First: OGC WMS advertising seven layers it could not draw and no endpoint able to serve them; INCOIS's own analysis holding cells no sea has held; the accent that made the console and the landing page read as two products. Then the audit itself - **fifteen false statements in documents and code**, among them a landing page promising a 60-day marker window against a real 5, a live dataset header three weeks out of date, four different adapter counts, a baked size wrong by a fifth, and `residuals.py` naming the 36-step bake while quoting the twelve-step one - and **six checks that could not catch what they claimed**. It raised 30 findings; 26 are closed and four were judged and left: a thirteen-site memo-guard refactor in `OceanScene`, the coverage refusal stated five times across two API modules, 2.1 MB of deliberately kept unused fonts, and splitting `CONTEXT.md`'s scope section out of the glossary, which waits until after 30 September | ADR 0012 amended, `test_surfaces_over_standards.py`, the widened `check_figures.py`, and the assertions added to `probe-hazard`, `probe-particles`, `probe-controls` and `probe-chrome` |

### The closed items that code still cites by number

A comment or a test that says "item NNN" means one of these. Everything else that was numbered is
in a round above, and the round's last column says where its detail went.

| Item | What it was | Closed by |
| --- | --- | --- |
| **104** | OGC WMS advertised layers the server could not draw, and no endpoint could serve them: seven Fields are one number per location and `servable_fields()` filtered on a list of names. Five of fourteen when it was written, seven of eighteen when it was fixed | `SURFACE_RENDER_KINDS` reading `FieldSpec.render`, `native_surface()`, `test_surfaces_over_standards.py`, ADR 0012 amended |
| **105** | WMS captioned seven layers as INCOIS's, Copernicus's current speed among them, and gave the five hazard Fields away as somebody else's published work | `api/standards.py`'s `PROVENANCE`, with no default at all, and `test_standards.py` failing on a Field with no entry |
| **122** | `residuals.py` quoted the buoy-to-float ratios as literals rather than reading `byKind`. The code was fixed and **the docstring's literals were not**, so they drifted again and the audit found them a second time | `residuals.field_bias`, and the docstring now says to read `byKind` instead of quoting it |
| **125** | `api/main.py`'s registry comment counted the two adapter lists beside them, and the count was wrong. Fixed once at "seven over eight", **wrong again at "eight over nine"** when `CopernicusBgcSource` joined the grid list | The comment carries no count now. `/api/sources` reads the lists |
| **134** | INCOIS's own temperature analysis holds cells no sea has ever held. Its close condition was somebody else's bake run, so it closed itself and this file listed it as open for six days | `oceanverity/plausibility.py`, and `manifest.masked` says how many |
| **136** | The colourbar switcher did nothing on any hazard Field: the Sheet, the Drape and the arrows are coloured on the CPU and the palette was not in their cache key | `paletteName` in all three keys, and `probe-palette.mjs` switching a Sheet and a Drape Field |

**Four of those are worth remembering as classes rather than as bugs**, because each came back in
a new costume:

- **A figure typed into prose cannot be checked by anything.** This is what `check_figures.py`
  exists for, and on 2026-09-22 it reported zero mismatches over a repository holding fifteen.
  It was too narrow, it read line by line so a figure split by a hard wrap was invisible, and it
  did not look at `api/`, the probes or `docs/NUMBERS.md`. All three are closed; the class is not.
- **A picture published by a map with a hole in it fails silently.**
- **"Cosmetic" is a claim, so measure it before believing it.**
- **A probe that collects, prints and exits 0 is a log, not a check.** Fixed across four probes in
  September and found again in one block of `probe-hazard.mjs` in the audit, which measured the
  speed under the cursor twice, explained in a comment why the two readings can disagree, and
  compared neither.
- **An impossible number is the tell, not the noise.** `probe-landing.mjs` reported the landing
  page's stat figure at **1.00:1 in both themes** - and one ground cannot give two different inks
  the same ratio, so the reading itself said the instrument was wrong. It was: the hero check
  composites ink over the rendered photograph, and the stat strip sits below the hero, so its box
  never landed on the frame being screenshotted. Measured directly the figure is `rgb(29,29,29)`
  on light and `rgb(236,236,234)` on dark, at alpha 1. **The page was never wrong.** The same
  check had already caught itself this way once, when it read `color` alone and reported one
  ratio for all six roles.
- **A control has to cost what the thing it controls for costs.** `probe-particles.mjs` compared
  two frames 500 ms apart and called the difference "background motion" - and the ray-marched
  water moves 3.16% of the frame in 500 ms, against a dot layer of 2.7%, so the check could not
  pass. With the water switched off for the pair it came back at 2.67% one run in two, because
  500 ms is not reliably longer than one software-rendered frame and the screenshot still held
  the layer that had just been hidden. **The measurement needed rethinking, not a threshold
  loosened.**

---

## Things that look artificial and are not

Each has been queried once, and "that looks made up" is the correct first reaction to all of them.

- **The drift pin does not move and the line does not animate.** The line is the whole trip at
  once, and it starts at the date on screen, which is why scrubbing redraws it.
- **Markers move when the bias map is on and you scrub away from the newest date, and there are
  more of them.** A residual belongs to the cast it was measured at, not to the date on screen.
  Switching the mode on opens it at the newest analysis, where 92% of them stay put. The map key
  says so, and so does the time axis while the mode is on.
- **The worst rows in the bias list share colours.** The scale saturates at the ninetieth
  percentile and everything past it clamps. The real gap is on the same row.
- **Hollow ringed markers** never measured that variable. Giving them the palette's midpoint
  would claim agreement with nothing.
- **A blank column in the vertical section** is land or sea floor, one grid cell wide because
  `Grid.column_at` refuses to blend across a Masked node. It is the data, not an artefact.
- **The deepest water in Temperature vs Normal is blank.** The atlas stops at 1500 m; the
  analysis runs to 2000 m. There is no normal to depart from.
- **Mean bias is almost exactly zero on all three Fields.** That is what gridding does to the
  floats the grid was built from, which is why the seventeen moored buoys are printed separately.
  Do not write "assimilate": the VAM analysis is gridding, not assimilation into a model, and
  whether it excludes buoys is unverified. `CLAUDE.md` carries the rule and `docs/plan/06` the
  research.
- **Drift separation reaches the distance travelled by 30 days and overtakes it after**, 106 km
  against 109 at 30 days and 212 against 168 at 90. A current field alone stops carrying
  information about a particular float quickly. Saying so is the feature.
- **The log-scale toggle looks marginal on INCOIS Cast Count and Depth of 26 degC** - measured
  margins 0.15 and 1.97 - and is **not a defect**. Cast Count's palette is a gradient; the
  "1, 2 and 3 casts painted as 4 or more" failure is Observation Coverage's, and coverage is
  refused by the banded check whatever its range. `transfer.ts` carries the table.

---

## Not defects, and the reasons are worth keeping

- **`page.goto` on a page that has already run the scene never fires `load` again** (was item
  101, open since 2026-09-06, closed 2026-09-26 with a cause). Four probes went red on this and
  nothing else - `probe-outreach`, `probe-palette`, `probe-case` and `probe-tour` - and in every
  one of them the checks before the timeout had already passed. `probe-case` matched IMD's track
  at 310 vertices against 310 from the file and completed all seven Montha steps first.

  **The measurement that identified it.** The same URLs, on a page that had driven the WebGL
  scene against a page that had not:

  | URL | Reused page | Fresh page |
  | --- | --- | --- |
  | `?tour=1&case=montha` | 60 s timeout | **0.1 s**, correct state |
  | `?dive=1&field=temperature&palette=curl` | 120 s timeout | **0.2 s**, correctly refused |

  So the app, the build and the URLs were never involved. Item 101's own recorded failures name
  "kiosk page load" and "the copied link", and **both of those are `page.goto` calls** - the
  table in it was pointing at the cause for three weeks in a column nobody read that way.

  **What the entry got right, and why the fix waited.** It refused the obvious repair because
  nobody had explained the failure, and said it wanted a deliberate decision rather than a
  tidy-up. That was correct: the two theories it recorded - browser degradation and overlapping
  `trueScale` loops - were both disproved by measurement, and a fix applied then would have been
  a test edited until it passed. `probe-palette.mjs` had already solved it once, for one of its
  own re-navigations, with the reasoning written beside it; the fix was to finish that thought.

  **Every re-navigation now takes a page that is fresh and alone.** Fresh, because a driven page
  never loads again. Alone, because opening the new page beside the old one fails the same way
  for a different reason: two pages fetching and decoding the same 223 MB of baked data at once
  under software rendering, and the second one's manifest never arrived inside 120 s. All four
  probes went green, `probe-outreach` on the first run.

  **The lesson is not about Playwright.** A failure that moves between steps looks like
  flakiness and was one thing all along, and the evidence needed to see it was already written
  in the entry. **A table of symptoms is worth re-reading for what the rows have in common.**

- **A tall control panel scrolls, and that is a panel and not a defect** (was item 47, closed by
  the owner's judgement on 2026-09-26). At 1366x768 the left bay is **663 px** and the panel
  spends **377 px** on group headers before a single control is drawn, so about 286 px are left
  for whatever is open. Re-measured 2026-09-23, opened one at a time beside Variable, both themes
  agreeing to the pixel: **5 of the 10 groups fit and 5 do not** - Colourbar by 156 px, Drift by
  143, the bias map by 510, Rendering by 39 and Instruments by 23. In 2026-09-07 it was 7 and 3.

  **Nothing regressed.** The panel got taller because a Field button gained a unit and a
  render-kind line under its name and the Field count went from 14 to 19. The bay did not move
  and the 377 px floor did not move. A reader scrolls inside a panel, which every console does,
  and the alternative - moving a control out of its group, or splitting a group - costs more in
  where-is-it-now than it buys in scroll. The bias group in particular is **597 px of
  measurements**, and a readout may not be approximated to fit a layout.

  **Two lessons from it are worth keeping, because both came back more than once:**

  - **A fold figure written down goes stale silently.** Two documents carried "615 - exactly the
    height available" through a round in which it was already 25 px wrong, then carried a 636 that
    was arithmetic rather than a reading. A number in prose has nothing that can fail.
  - **Counting rows is not measuring height.** The two-column grid for the colourbar alternates
    should have halved 132 px by arithmetic and returned **12 px** measured, because halving the
    cell wraps all five labels. The same mistake called Rendering 62 px over when it fitted.

- **`drift.ts` and `section.ts` duplicate science that also lives in Python.** Deliberate, and
  the only two. Held to the pipeline by `probe-drift.mjs` and `probe-section.mjs` - median
  0.331 km over 101 days, worst gap 5.07e-5 degC over 1,102 values. ADR 0015. **Do not add a
  third without the same harness.**
- **Fourteen scene colours are written twice**, in `SCENE_COLOURS` and in `styles.css`, because
  the geometry is drawn in WebGL and the swatch beside its name in the map key is drawn in CSS.
  `probe-chrome.mjs` compares all seven pairs in both themes now and fails on a one-digit drift,
  so the duplication is measured rather than trusted.
- **The bias map is not AI and has no confidence score.** It is the mean and RMS of residuals
  the bake already computed.
- **The upload is the only network call the frontend can make**, and only when a user drops a
  file.
- **The WOA climatology is a baseline and never a value.** Not in the Variable selector. ADR 0016.
- **The particle layer's share of the frame is a range, not a point** (2.05% to 2.56% over four
  runs on one unchanged build). The population is seeded with `Math.random()`; the probe asserts
  a floor and that the layer beats a still-frame control, never an exact figure. Since
  2026-09-23 it takes its pair with the water switched off, so the share it prints is the layer
  over bare ground and not the on-screen share.
- **The two-seas Explore card carries three typed figures** - 3.0 kg/m3, 3.7 PSU and the
  temperature contrast that changes sign - and they are the only figures on an Explore card not
  read from the bake at runtime. The boxes, the depth and the method are written down beside
  them, and they were re-verified exactly on 2026-09-23. Re-run them after a bake.

---

## How to check any of this

The full command list is `CLAUDE.md`'s own Commands block. The short version, with a preview
server on 4173 and the API on 8000:

```bash
cd pipeline && ../.venv/Scripts/python -m pytest -q          # 511 tests
cd pipeline && ../.venv/Scripts/python scripts/check_figures.py
cd web && npm run typecheck && npx vite build
cd web && for p in landing guide tour controls hazard bias particles isolate palette \
                   chrome case outreach requirements drift section upload; do node probe-$p.mjs; done
```

`probe-section` and `probe-upload` need the API; the other fourteen do not.

**Check what is holding a port before trusting a result.** A `uvicorn` and a `vite preview` from
previous days were both found still listening during the audit, and two probes ran against
yesterday's API before anyone noticed.

**Run the API-needing two separately, and stop the API afterwards.** `probe-outreach` failed on
`page.goto("app.html?kiosk=1")` with a 60 s navigation timeout, twice in a row, while `uvicorn`
was up on 8000 - and **failed identically on a clean `HEAD` build**, which is how it was ruled
out as a regression rather than argued about. With the API stopped it passes first time. The
server holds the native Grids in memory and competes with swiftshader for exactly the
re-navigation that rebuilds the whole scene, which is the shape of item 101. So the contention
warning is not only probe-against-probe: **a probe that does not need the API loses to one that
is running.**

**And every probe can go red.** Four of them used to collect what they measured, print it and
exit 0 regardless, which is why "green" meant nothing for those four. They assert now, and the
audit found and closed three more gaps of the same shape: a block of `probe-hazard.mjs` that
printed two readings of the same number and compared neither, a check in `probe-particles.mjs`
that passed when its own scene hook was missing, and a rule in `probe-controls.mjs` that could
only ever fire alongside another. **Before adding a probe, make it fail on purpose once.**
