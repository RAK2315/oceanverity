# Known defects and open suspicions

**Worked through 2026-09-03, revisited four times on 2026-09-04, again on 2026-09-06, swept
whole-repository on 2026-09-10, fixed on 2026-09-11, and 104 and 134 closed on 2026-09-21. Two
items are open; 136 are fixed.** The open two are 44 and 101, which both predate the
2026-09-10 sweep and are both open on purpose: 44 is a judgement about prose that a probe would
guess at worse than a person, and 101 is a flaky probe whose two proposed causes were each
disproved by measurement. Items 104 to 133 came from a read-only audit of every surface on
2026-09-10 - `pipeline/`, `api/`, `web/src`, the four pages, the probes, the tests, the Markdown
and the decision records. **The header count has been wrong before**: it said "three items are
open" over two, and the numbering had reached 103 while a handoff said 102. Count the `- [ ]`
markers before trusting this line.

**134 closed itself and nobody noticed for six days.** It said it would close "when that bake's
`manifest.masked` says so", the 2026-09-15 bake ran the mask, and this file went on listing it
as open. A defect whose close condition is somebody else's run needs checking after that run;
see the entry.

The fixed ones are summarised rather than listed, which is this file's own convention: a
defect whose measurement has been folded into `CLAUDE.md`, an ADR or a probe does not need a
paragraph here, and a file that is 90% solved problems is a file nobody opens to find the two
that are not.

The ranking is the one this file has always used:

1. **Tells a user something false.** A wrong sentence on screen costs more than a missing feature.
2. **Data quietly discarded, or quietly invented.** Silence about what was dropped, or about what
   was assumed, is the same fault one level down.
3. **Labels, presentation and performance.** Cheap to fix, and "cosmetic" is worth measuring
   before believing.

---

## Still open

- [x] **102. The exhibition screen kept whatever camera one question zoomed to. Fixed 2026-09-07.**
      Reported as "the kiosk zooms in on a particular spot, not where I set the view".

      `focusOn` hard-sets the camera to a fixed radius and `panTo` preserves whatever distance it
      finds, so the one question that zooms to a float - *What does one robot float actually do?* -
      left **every question after it** framed at float distance, with nothing that would ever put
      it back. Measured: `focusOn` took the camera from **79.9 units to 22.1**, and the next
      `panTo` came back 22.1. An operator who set the screen up on a wide view of the basin got
      that view for four questions and a close-up for the rest of the day.

      Two halves, because either alone leaves the other. The loop remembers the pose it opened on
      and restores it before each question, and it is handed a `focusOn` that pans - so a question
      can neither take the framing away nor leak a distance forward. Restoring between questions
      is safe because the loop already pauses while anybody is touching the screen, so a visitor's
      own drag is never undone under their hand. Measured after: **79.9 held across all six
      questions, worst change 0.0 units.**

      Explore keeps the zoom. There a reader pressed the question deliberately and the comparison
      panel is on screen to read; on an unattended screen it is a camera move nobody asked for.

- [x] **103. Playing the timeline with the bias map on looked like a broken animation. Fixed
      2026-09-07 - by saying so, not by moving anything.**
      Reported as "when I hit play it works, but with *Colour instruments by disagreement* enabled
      the Argo animation is not happening, they pause at the position they are at".

      **The markers are right and must not move.** Every instrument on the bias map is drawn at
      the cast its own comparison was taken from, across all thirty-six analyses, because a residual
      measured at one position on one date is a number on the wrong water anywhere else. Measured:
      marker 0 sits at 62.447 E, 17.748 N at step 2 and at exactly the same place at step 11.

      So this was never a motion defect. It was a **communication** one, and the information was
      already on screen in the wrong place: the map key says "each one is where its own comparison
      was taken ... not where it was on this date", and the map key **folds, and is remembered
      folded per browser**. A reader with it shut sees a field animating and every instrument
      standing still, with nothing anywhere admitting why.

      The time axis says it now, in `--secondary`, whenever the mode is on: **"Instruments pinned
      to their own cast dates"**. A caveat belongs beside the control that provoked the question,
      not two panels away behind a disclosure somebody shut last week.


- [ ] **101. `probe-outreach.mjs` fails intermittently, and the failure moves between steps.**
      Found 2026-09-06 while shortening the kiosk hold from 20 s to 5 s. **The kiosk itself is
      fine** - soaked for three minutes, all **8 questions played**, the WebGL context stayed
      alive, and a heavy page still loaded in 3.2 s afterwards. It is the probe that is unstable.

      Six runs, and the failing step is not the same one twice:

      | Kiosk hold | `trueScale` cancellation | Result |
      | --- | --- | --- |
      | 5 s | no | timeout at step 5 (the copied link) |
      | 5 s | no | timeout at step 5 |
      | 5 s | no | timeout at step 3 (kiosk page load) |
      | 20 s | no | **clean** - no timeout, truescale passed |
      | 5 s | yes | no timeout, but the truescale check failed |
      | 5 s | yes | timeout at step 3 |

      The URL that times out loads in **1.7 s in a fresh browser**, so it is not the page. The
      probe drives **one reused page** through eight full scene rebuilds, then kiosk, then a
      deeplink round trip; and its own source already says the truescale check "ran fine and then
      failed a run later ... under software rendering that is a coin toss".

      **Two theories were proposed and both were disproved by measurement**, which is why this
      entry has no cause in it: browser degradation (the soak's heavy page load refutes it) and
      overlapping `trueScale` loops (the timeout came back with the cancellation in place). The
      5 s hold correlates with the flakiness but does not explain it, and n is small.

      **The obvious fix was deliberately not applied.** Step 5 tests that a copied link
      round-trips, which has nothing to do with the state steps 1 to 4 leave behind, so giving it
      a fresh page would probably make it green and would arguably be more correct. Editing a
      test until it passes, against a failure nobody has explained, is the move this file exists
      to discourage. It wants a deliberate decision, not a tidy-up.

      Related and kept: `trueScale()` in `web/src/explore.ts` now cancels a run still in flight
      before starting another. A 9 s animation on a 5 s cadence really did stack loops fighting
      over one value. That is a real defect and the fix stands on its own; it is simply not the
      cause of this one.

- [ ] **44. Nothing checks that a caption still describes its picture.**
      Every landing-page and README picture carries written prose beside it, and some of it names
      colours - *"warm yellow at the sea surface fading through orange to deep violet at 2000
      metres"*. A theme change, a re-capture or a chosen frame makes that false and nothing
      notices.

      **The frames and the pipeline are solved; the prose is not.** Every picture was re-chosen
      on 2026-09-04 and every caption beside one was rewritten against the frame it now sits next
      to - but that was a person reading, not a probe. `probe-landing.mjs` checks a picture
      *exists*, *loads*, and *follows the theme*; it cannot check that the sentence under it is
      true. **This stays open on purpose**: it is a judgement about prose, and a probe that
      guessed at it would be worse than none.

      **The fourth pass found two instances and fixed both, and the fix is the mitigation this
      entry asked for: describe the role, not the colour.** The README's lead picture was cropped
      so hard that the comparison panel was sliced off at the right edge - "Argo 790..." and a
      fragment of "99[6] DEPTHS COMP..." - under a caption promising "on the right a panel
      comparing one float's measured temperature against the model's at 996 depths". And
      `scripts/dossier.html`, `docs/demo/script.md` and `docs/demo/beats.md` all said *"green is
      the instrument, dashed blue is the model"* when `styles.css` paints `--observed` teal
      (`#00666e` light, `#64d7e3` dark), `--model` grey and dashed, and the difference band pale
      red. All four now say *solid line*, *dashed line* and *the band between them*, which is
      true in both themes and survives a re-capture. **A caption that names a colour is a caption
      with a shelf life.**

- [x] **47. Two control groups open scrolls the left panel. Fixed 2026-09-06.**
      It took two rounds and the first one made it worse, which is the part worth keeping.

      **Round one made the deficit bigger, correctly.** Lifting the timeline off the source
      credits meant the panel had to clear the credits too, so its `max-height` went from
      `calc(100% - 118px)` to a measured expression - and at 1366x768, where the credits wrap to
      two lines, the panel gave up 50 px. The deficit was never the 44 px the old figures imply:
      re-measured, it was **94 px**, because the available height had gone 678 -> 628 while
      nobody was looking.

      **Round two closed it, and then the console redesign reopened it twice more.** The frame
      rebuild moved the foot from a floating pill to a band, which cost the bay height again
      (31 px), and reclaiming that left 11 px. Final measurement at 1366x768, with the bay at
      **615 px**: all closed **347**, Variable alone **446**, **Variable and Colourbar 615 -
      exactly the height available**, Variable and Depth slice 534, Variable and Instruments 557.

      Where the height came from, in order of size: ten group headers at 10 px of vertical
      padding were 348 px of pure chrome, and at 7 px they are 300; the date stamp in the time
      axis went from two stacked lines to one, which is 14 px off the foot band; and the rest is
      a pixel or two each from body padding, slider margins, the colourbar scale and the tab row.
      **No control was removed and no explanation was cut** - `probe-guide.mjs` still measures a
      median of 112 words across all 44 entries, unchanged.

      **Narrowed on 2026-09-06, not closed:** `Colourbar + Rendering` scrolls by
      53 px, down from 106, after Ray steps and Show volume moved into their own `Quality` group.
      The bias group came down from 1,293 px to 918 the same day. What is left in both is
      measurements, and a readout may not be approximated for layout - see item 101 and `CLAUDE.md`.

      **Reopened wider on 2026-09-07, and the figures above were already stale before that.**
      Two things happened in opposite directions and the second is much larger than the first.

      Folding the source credits took the foot band from 48 px to 28 and **gave the bay 20 px**,
      615 to 636. But the "Variable and Colourbar 615 - exactly the height available" line was
      **never re-measured after the round that produced it**: measured against `HEAD` before this
      session changed anything, that pair was already **641 px against a 616 px bay, 25 over**.

      Then the colourbar switcher landed, and it **cost the Colourbar group 139 px** - five or six
      palette buttons in a vertical list, each carrying a 46 px swatch.

      **Paid for on 2026-09-07 by folding the alternates. 108 of the 139 are back.** The bay is
      **635 px**, measured as the panel's own `clientHeight` at its cap; the 636 both documents
      carried was arithmetic (615 plus the 20 the credits fold returned) and never a reading.
      `max-height` cannot be read instead - it is a `calc()` and `getComputedStyle` returns it
      unresolved, which is a `NaN` that formats as a number. Measured at 1366x768, **in both
      themes, which agree to the pixel**:

      | Panel state | Before | After | Against a 635 px bay |
      | --- | --- | --- | --- |
      | all groups closed | 377 px | 377 px | fits |
      | **Colourbar alone** | **680 px** | **572 px** | was 45 over, now fits |
      | Variable alone | 477 px | 477 px | fits |
      | Variable + Colourbar | 780 px | **672 px** | over by 37 |
      | Colourbar + Rendering | 806 px | **698 px** | over by 63 |
      | bias | 918 px | 918 px | over by 283 |
      | everything open | 2,115 px | 2,007 px | over by 1,372 |

      **The sharper statement of the bug was never "the Variable pair is 144 over".** It was that
      the Colourbar group had become the one group in the panel too tall to open **on its own** -
      333 px against the 258 px left once the 377 px floor of group headers is paid. It opens
      alone with 63 px to spare now.

      What went in: the five labelled swatches (132 px) fold behind one 24 px row that carries the
      chip and the name of the colourbar actually on screen. That row **reports while it is shut**,
      which is the same rule that lets a collapsed group keep its readout - a bare "more"
      affordance would have hidden the one line in the group that says what is drawn.
      `store.paletteAlternates` holds the fold, and `selectField` deliberately leaves it alone
      where it resets `paletteOverride`: this is a panel preference, not a data choice.

      **The two-column grid lost on measurement, and by far more than arithmetic predicted.**
      Five rows become three, so counting rows says it halves 132 px to about 83 - 49 px back.
      Measured by forcing `grid-template-columns: 1fr 1fr` onto the real list: the list goes
      132 px to **120**, which is **12 px**, against the fold's 110. The cell drops from 291 px
      wide to 144, the widest label needs 173 px of text and is left about 83, and **all five
      labels wrap to two lines** - three double-height rows are barely shorter than five single
      ones. `styles.css` had already argued against the grid and was right for a different reason
      than it gave: not four smudges, four wrapped labels. **Counting rows is not measuring
      height**, which is the same mistake as calling Rendering 62 px over below.

      **`probe-palette.mjs` and `probe-chrome.mjs` had to move with it, and one of them could
      have passed vacuously.** The probe read `.palette-choice button`, which after the change
      matches only the folded row - so the fifteen-Field offer check would have read one button
      per Field and reported it as correct. It reads `.palette-list button` now and unfolds first,
      which is exactly the lesson `.colourbar` and the shut Colourbar group taught a round ago,
      one level further in. It also gained an assertion that the folded row names the colourbar
      actually drawn, and **that assertion was made to fail on purpose**: pinning the row's label
      to a constant turned 13 of the 15 Fields red with the drawn palette printed beside the
      claimed one. `probe-chrome.mjs` gained `.palette-current` and `.palette-list button` as text
      roles - neither the old chooser nor the new one had ever been contrast-checked. Measured:
      16.91:1 and 9.12:1, both themes.

      **What is left is older than the switcher and is structural.** The floor is 377 px of group
      headers before a control is drawn, leaving 258 px. Opened one at a time beside Variable and
      **measured rather than added up** - the arithmetic got Rendering wrong, calling it 62 px over
      where the panel fits it with 32 to spare - **7 of the 10 fit and 3 do not**: Colourbar by 37,
      Drift by 73, the bias map by 383. Closing the last 37 needs a control removed or the 30 px
      group header cut to 26, which is a design token and a click target at the WCAG 2.2 floor.
      Neither was done unilaterally. **Narrowed, not closed.**

      The other lesson is the one this file exists for: **a fold figure written down goes stale
      silently.** Two documents carried "615 - exactly the height available" through a round in
      which it was already 25 px wrong, and then carried a 636 that was arithmetic rather than a
      reading, because a number in prose has nothing that can fail.


- [x] **104. OGC WMS advertised seven layers the server could not draw, and no other endpoint
      could serve them either. Fixed 2026-09-21, by serving them.** Deferred by the user on
      2026-09-11 - "we will come back to this" - and it grew while it waited.

      **It was five of fourteen when this entry was written and seven of eighteen when it was
      fixed.** `oxygen_floor` and `fronts` arrived at the 2026-09-15 bake, and nothing was
      watching the class, because the refusal was a list of names rather than a rule. Measured
      over HTTP on 2026-09-21, before: `GetMap` on `d26` returned HTTP 404 with the body
      `{"detail": "no grid for d26 at timestep 35"}` - JSON, from an endpoint whose own
      capabilities document promises `<Exception>XML`, which a WMS client shows as nothing at
      all.

      **They did not need recomputing.** This entry said their Grids "can be recomputed offline
      from the temperature and salinity `.npz`". They were already on disk at full precision:
      `web/public/data/surfaces/` holds 252 files of 2016 float32 values, and 2016 is exactly
      the 56 x 36 analysis lattice. The bake never wrote a second copy because nothing had ever
      asked for one. `native_surface()` in `api/main.py` reads the served file, which is
      legitimate in a way reading a Volume would never be: a surface *is* the analysis lattice,
      not a quantised depth-warped picture of it.

      **The shape was the real decision.** This entry framed the alternative as refuse-or-serve
      and noted that serving would mean "a one-Level depth axis that claims the value varies
      with depth". CF does not require that: a quantity with no depth is a
      `(time, latitude, longitude)` array with no vertical coordinate at all. So
      `oceanverity/grid.py` gained a `Surface` beside `Grid` - deliberately not a Grid with one
      Level, because the difference leaves the building - `cf.as_dataset` builds 3D from it,
      `dap.py` needed nothing at all since it was already generic over dims, and `wms.py` got
      `_plane()` and a per-layer elevation dimension in place of one list for the whole service.

      **Measured after, over HTTP.** All 18 layers draw; 11 advertise an elevation dimension and
      the seven surfaces advertise none; `GetFeatureInfo` on a surface reports `"depth": null`
      rather than zero metres; `elevation=5` and `elevation=500` give byte-identical images on
      `d26` and different ones on `temperature`. Read back with real clients, not our own bytes:
      `xarray` opens `/api/netcdf/d26/0` and `xarray` with `engine="pydap"` opens
      `/opendap/d26/0`, both giving 80.711 m at 12.5 N 72.5 E, and the served array matches
      `d26_000.bin` exactly.

      **And the other half, which was never in this entry.** `field_spec` raises
      `HTTPException`, which FastAPI renders as JSON, and the `/wms` handler caught only
      `wms.WmsError`. So even a genuinely wrong request came back unreadable. It returns a
      `ServiceExceptionReport` now; checked with `layers=coverage`, which is the one Field still
      refused and now says so in XML.

      `test_surfaces_over_standards.py`, 16 tests, red first. The one that matters is
      `test_every_field_is_either_served_or_refused_by_name`, which is this defect written as
      the rule it broke rather than as the seven names it broke it on.

- [x] **134. INCOIS's own temperature analysis holds cells no sea has ever held. Closed by the
      2026-09-15 bake; confirmed 2026-09-21.**
      Found by measuring the Suspected entry about Temperature vs Normal: recovering the atlas
      value as analysis minus departure shows **the atlas is fine and the analysis is not** -
      4.84 degC at 20 m in the Persian Gulf in July, 45.17 degC at the same node in May, 48.66
      degC at 30 m. Every such cell is on the region's northern edge, 24.5 to 25.5 N and 52.5 to
      61.5 E, and most sit at 20 to 30 m, beneath a surface that should be the warmest water in
      the column. **No Collocation touched one**, checked both as a sampled value and as a
      bilinear corner at the comparison's own Timestep, so the bias map and every residual are
      clean. What read them is the tooltip, the section and CF, OPeNDAP and WMS.

      **The user chose mask-and-count on 2026-09-11.** `oceanverity/plausibility.py` masks
      temperature outside **-2.5 to 38 degC** - below seawater's freezing point, and beyond
      37.6 degC, the verified in-situ record for the Persian Gulf - in both INCOIS analyses, at
      the door of the bake, so density, both anomalies, the spread and the hazard Fields inherit
      the absence. The bake writes `manifest.masked` (bounds, a count per source, the reason),
      and `provenance.html` prints it in the pipeline table - checked in the browser both with
      the block and without it. Six tests in `test_plausibility.py`, red first. **On the shipped
      Grids it takes 25 cells** (23 hot, 2 cold). The first figure written here was 37, at a
      36 degC bound this file chose before looking up the record; the hot values run
      continuously from 35.8 to 48.7 with no gap, so 12 cells between 36 and 38 degC are kept
      as suspicious rather than masked.

      **Why it was not applied to the shipped data at the time.** A bake takes the newest 36
      analyses and re-fetches Argo, so re-baking moves the window and every measured figure in
      the build. Patching the shipped files instead would mean re-running six stages of the bake
      by hand - the Grids, density, both anomalies, the spread, the hazard sheets, the Volumes
      and their ranges - which is a partial re-bake that could quietly disagree with a real one.
      So the next real bake applies it, and this item closes when that bake's `manifest.masked`
      says so.

      **It said so, and nothing checked.** The 2026-09-15 bake ran the mask and this file went
      on listing the item as open for six days. Confirmed on 2026-09-21 from the shipped build:
      the manifest carries `masked` with 25 temperature cells against a `-2.5 to 38` bound and
      0 in `mccreary_temperature`, which is exactly what this entry predicted; and the maximum
      across all **144 shipped temperature Grids is 34.40 degC**, so the 45.17 and 48.66 degC
      nodes are gone from the data a reader can reach.

      **The lesson is about the close condition, not the mask.** "Closes when somebody else's
      run says so" puts the check outside the session that can do it, and no bake runs a pass
      over this file. A deferred item whose trigger is a bake needs re-reading after the next
      bake, which is now a line in `docs/plan/06`'s order of work.

**Closed 2026-09-11** - one line each; the measurement lives where the line says.

- [x] **105.** WMS captioned seven layers as INCOIS's, Copernicus's current speed among them. `api/standards.py`'s `PROVENANCE` names the source of every Field, the service `<Abstract>` in `wms.py` agrees, and `test_standards.py` fails on a Field with no entry. Checked over HTTP: 14 of 14 layers correct.
- [x] **106.** Ten Fields went out over CF dimensionless with their key as their name, and the NetCDF `institution` said INCOIS for Copernicus data. `api/cf.py` covers all 15 with UDUNITS units, short `long_name`s, a variable `comment` and a per-Field source; `test_standards.py`. `current_speed` takes `sea_water_speed`; nine Fields stay nameless on purpose and the comment says why for each.
- [x] **107.** Screen-reader text called every instrument an Argo float. `App.tsx` announces by kind through `reportingByKind()`; the pooled `reportingCount()` is gone.
- [x] **108.** The bias card showed `collocation.jpg`. `PUBLISH_MAP` publishes `bias.jpg` to the site with a `light` override, the card points at it, and `probe-landing.mjs` records it in `FIXED`. Publish dry-run: 60 of 61 outputs already identical, one file written.
- [x] **109.** `requirements.html`: 43 -> 44 controls (twice), sixty -> thirty seconds, 234 -> 266 instruments, twelve -> thirty-six analyses.
- [x] **110.** Landing page: nine -> seventeen buoys, four months -> a year, sixty -> thirty seconds (twice, the second in the Kiosk card the audit missed).
- [x] **111.** `collect_facts.py`'s one literal row is derived by replaying `positionAt` over all 36 steps: 192 to 221 floats, 5 to 14 buoys. `FACTS.md` regenerated; no other row moved.
- [x] **112.** `README.md`: 15 -> 21 routes, in the diagram and the table, box alignment unchanged.
- [x] **113.** The guide's spread bullet is tokens now, filled from `manifest.anomalySpread`, which `anomaly.spread_by_level` computes and `bake.py` writes; `refresh_anomaly_spread.py` filled the shipped manifest from the Grids on disk. 0.63 / 1.56 / 0.07 degC, peak at 100 m, five tests.
- [x] **114.** The manifest's stale "four months" description. `scripts/refresh_field_prose.py` rewrites prose from the specs; one string changed, every other key identical.
- [x] **115.** ADR 0015's horizon rows re-read off the manifest, and the paragraph now says what they say: past a month the separation **exceeds** the travel, by 15% at 60 days and 29% at 90. The audit's 30-day row (106.0 / 109.1) did not reproduce; the manifest says 105.0 / 108.1.
- [x] **116.** ADR 0016: +0.074 degC (the sign flipped), 2.051, ±3.547, and twelve monthly normals, not four.
- [x] **117.** `DESIGN.md`'s retired 636 px fold table replaced by a pointer to `CLAUDE.md`'s, which is the only copy.
- [x] **118.** 43 -> 44 in all eight documents. `probe-guide.mjs` renders `Object.keys(GUIDE)` instead of a hand list that had never rendered `performance`, and asserts the 44.
- [x] **119.** `--timesteps` defaults to 36, and `CLAUDE.md`'s command says 36 minutes and that it clears the committed bake.
- [x] **120.** The glider reader converts decibars with `pressure_to_depth` at the cast's own latitude. `_read` split into fetch and `_parse`; three tests, red first.
- [x] **121.** `coverage.py`'s `BANDS` now rests on what each band counts, not on a split a re-bake falsified. Re-measured: 2,441,628 voxels, median 3, maximum 19, split 10.2 / 13.7 / 28.4 / 47.6, and 1/3/10 would hold 7.0%.
- [x] **122.** `residuals.py`: 266, seventeen buoys, 5.5x / 7.7x / 5.4x, 249 floats, read off `byKind`.
- [x] **123.** `probe-bias.mjs` walks the first, middle and last step of the manifest's own timeline.
- [x] **124.** `probe-drift.mjs` drops its pin on the last analysis, read off the manifest.
- [x] **125.** `api/main.py`: eight registered adapters and why the two lists differ from `CONTEXT.md`'s; five profile providers; 8,460 casts from 259 platforms. The latent `KeyError` became item 135, closed below.
- [x] **126.** `anomaly.py`'s two sets of spread figures replaced by `spread_by_level`; the `Z_THRESHOLD` argument re-measured (|z| 1.62 at p90, 2.57 at p99, 4.1% of cells past 2.0) and still holds; 404 features, 11.2 a step.
- [x] **127.** The comment sweep: every Python, TypeScript and HTML row, plus `CONTEXT.md`, the demo script, `DECK.md`, ADRs 0010, 0012 and 0014, and `scripts/dossier.html`, re-rendered to the PDF. Figures that justified a decision and cannot be re-taken offline are dated rather than replaced. **One the audit missed was on screen**: Depth of 26 degC's "Try this" said "breathe across four months".
- [x] **128.** The five dead exports and the orphaned `Texture` import, each re-traced to a single occurrence before deletion.
- [x] **129.** `on-globe` removed from `MapKey.tsx`.
- [x] **130.** `deeplink.ts` points at `probe-outreach.mjs` and carries the real counts; `probe-bias.mjs`'s pointer reads as history.
- [x] **131.** The four unused imports, the identical `dap.py` branches, and `parse_constraint`'s parts named by position; pyflakes clean over all four trees.
- [x] **132.** Two uncalled guide figures removed; `test_palettes.py` reads the shipped range and table (and fails with a 0..14 table, measured); Explore's "a minute" comments; the defaults doc block reattached; "four sources of truth".
- [x] **138. The requirements page and the work plan both said Godas ends eleven months before this bake's window. It is under three.** Found while merging the requirements-page restyle. Godas 2025 ends 2025-05-22 and the window opens 2025-08-10, which is 80 days. Eleven months was right for the four-month bake and was missed when the window went to a year; its neighbour in the same table, the GO-SHIP row, was corrected in that sweep. Three places: `web/requirements.html`, and `docs/plan/04-ps-update-2026-09.md` twice. The reason Godas is refused is unchanged - it has no data inside the window.
- [x] **137. Switching on the bias map moved every marker, and read as a bug.** Reported by the user at 30 Dec 2025, where the 199 markers on screen moved a median 258 km (1,414 km at worst) and 52 appeared, because each marker is drawn at the cast its comparison was taken from and 206 of 251 were taken at the last two steps. The markers were right. What changed is the date the mode opens on: `store.setBiasMode(true)` moves the timeline to the newest analysis, where 92% of markers do not move at all, and the checkbox, the tour and Explore all go through it. Checked through the real checkbox: step 14 to 35.
- [x] **136. The colourbar switcher did nothing on any hazard Field.** Reported by the user. The store took the choice and the legend repainted, but the Sheet, the Drape and the current arrows are coloured on the CPU and rebuilt only when their cache key changes, and the palette was not in the key: measured 0.1% of the band repainted on all five against 39.3% on Temperature. `paletteName` is in all three keys now; after, 5.8% to 9.7% on the four sequential hazard Fields and 10.8% to 79.4% of the barrier layer's drape texels by alternate. `probe-palette.mjs` switches a Sheet and a Drape Field as well as Temperature, and would have gone red on the old build.
- [x] **135.** `CopernicusCurrentsSource.fetch_grid` raised `KeyError` on `current_speed`, the one key its own `fields()` declares. It serves every declared key now and refuses an unknown one by naming what it serves; `test_copernicus.py`, five tests against an in-memory dataset, red first.
- [x] **133.** `standards.py`'s docstring no longer calls coverage servable; `shot.mjs`, `check-pdf.mjs`, eleven scratch probes and the leftover worktree and its merged branch removed.

---

## Suspected, not confirmed

None open. The six that were here were measured on 2026-09-11 before anything was changed:

- **The ±22 degC cells in Temperature vs Normal** - confirmed, and the atlas is not at fault: it is
  INCOIS's own analysis. Now item 134.
- **"0.8 degC warmer"** - the audit's boxes reproduce 0.82 degC, 3.03 kg/m3 and 3.68 PSU as the
  **annual mean**, but the temperature contrast runs -0.97 to +3.04 across the year and changes
  sign, while density and salinity never do. The sentence leaned on the unstable one, beside a
  view of one Timestep where it measures +0.42. Rewritten on the stable two, with the boxes
  written down in `explore.ts` and `guide.ts`.
- **The log gate is marginal on Cast Count and D26** - measured margins 0.15 and 1.97, and **not a
  defect**. Cast Count's palette is `tempo`, a gradient; the "1, 2 and 3 casts painted as 4 or
  more" failure is Observation Coverage's, and coverage is refused by the banded check whatever
  its range. Tipping either Field over would offer log on a continuous Field that starts near
  zero, which is what the rule permits. `transfer.ts` carries the re-measured table.
- **"13 of the 15 variables computed or fetched here"** - meant "INCOIS publish two, the rest are
  ours", and INCOIS publish four. Now "4 published by INCOIS, 11 computed here", matching the
  `PROVENANCE` table the WMS serves.
- **ADR 0011's supersession note at its foot** - a banner at the head now points at 0013.
- **Six test modules with no docstring** - written, from what each module's tests assert;
  `tests.json` regenerated and no row on `provenance.html` says "Covered by this module".

---

## Fixed, in summary

**132 defects across five rounds.** Every measurement that was worth keeping is now in one of
four places, which is why they are not repeated here: a rule in `CLAUDE.md`, a decision record in
`docs/adr/`, a probe that fails if it comes back, or a test.

| Round | What it was | Where the detail lives |
| --- | --- | --- |
| **2026-09-03**, 51 items | The September survey. The bias map pooling assimilated floats with unassimilated buoys; the drift score measured on days the current field does not cover; casts drawn on a section they were not in; a corridor measured against a rhumb line where the drawn line is a great circle; a masked corner refusing a whole column; render hints leaking between Fields; the log scale offered where it means nothing | ADRs 0015-0017, and the rules block in `CLAUDE.md` |
| **2026-09-04**, first pass, 12 items | The isosurface sharing the haze's coverage floor and putting sheets over India; current trails coloured by the value they sit on; a capture borrowing kiosk mode; volume controls hidden on a Field that draws a volume; `getBoundingClientRect()` on a hidden panel returning zeros | New rules in `CLAUDE.md`; `probe-hazard.mjs`, `probe-guide.mjs`, `probe-bias.mjs` |
| **2026-09-04**, second pass, 8 items | Two landing cards with alt text over an empty panel; a hero unreadable on light at 1.27:1; five hazard variables that all opened the same way; a heading claiming sixteen cards over fourteen; the deck two rounds stale | `probe-landing.mjs`, and three more rules in `CLAUDE.md` |
| **2026-09-04**, third pass, 8 items | Four folders holding overlapping copies of the same pictures; a publish silently replacing thirteen dark images with light ones; pictures that did not follow the theme toggle; `probe-upload.mjs` unable to run from a clone; the deck's numbers with nothing to check them against | `assets/screenshots/` as the single source; `pipeline/scripts/collect_facts.py` and `ppt/FACTS.md` |
| **2026-09-04**, fourth pass, 21 items | **The prose sweep.** `provenance.html` printing the superseded "currents are an image" line with `undefined m` in it; two requirements links labelled *Open a float comparison* that started the guided tour; the demo script reading numbers off the screen that the screen contradicts, and claiming all three variables share a worst 5-degree box; a landing tile pairing a median RMS with a mean absolute bias under a caption saying they were the same distribution; the retired 202-float drift score; 3,718 Argo casts that are 3,077; `longitude = 46` hardcoded on the page whose banner says nothing is; **four of the thirteen probes that could not go red**; `render-dossier.mjs` writing a PDF with three broken images | `CLAUDE.md`'s Commands block, the four probes' own assertions, and the rules below |
| **2026-09-11**, 32 items, and item 134's mask built | **The audit's list, and the six suspicions.** Copernicus current speed attributed to INCOIS over WMS, and the five hazard Fields captioned as somebody else's; ten Fields served over CF as dimensionless; a guide bullet quoting a spread from a bake that is gone; ADR 0016 with the sign of its mean backwards; a `--timesteps` default that would have replaced the committed bake with a third of it; decibars in a depth axis; a probe that never rendered one of the 44 guide entries; and the comment sweep a year-long bake needed | `test_standards.py`, `spread_by_level` and its tests, the glider `_parse` tests, `test_copernicus.py`, `probe-guide.mjs`'s count, the two `refresh_*` scripts, and the one-line entries above |

**Three of those are worth remembering as classes rather than as bugs**, because each came back
in a new costume: *a figure typed into prose cannot be checked by anything*; *a picture published
by a map with a hole in it fails silently*; and *"cosmetic" is a claim, so measure it before
believing it*.

---

## Things that look artificial and are not

Each has been queried once, and "that looks made up" is the correct first reaction to all of them.

- **The drift pin does not move and the line does not animate.** The line is the whole trip at
  once, and it starts at the date on screen, which is why scrubbing redraws it.
- **Markers move when the bias map is on and you scrub away from the newest date, and there are
  more of them.** A residual belongs to the cast it was measured at, not to the date on screen.
  Switching the mode on now opens it at the newest analysis, where 92% of them stay put. The map
  key says so.
- **The worst rows in the bias list share colours.** The scale saturates at the ninetieth
  percentile (0.49 degC on the 36-step bake) and everything past it clamps. The real gap is on
  the same row.
- **Hollow ringed markers** never measured that variable. Giving them the palette's midpoint would
  claim agreement with nothing.
- **A blank column in the vertical section** is land or sea floor, one grid cell wide because
  `Grid.column_at` refuses to blend across a Masked node. It is the data, not an artefact.
- **The deepest water in Temperature vs Normal is blank.** The atlas stops at 1500 m; the analysis
  runs to 2000 m. There is no normal to depart from.
- **Mean bias is almost exactly zero on all three Fields.** That is what an assimilating analysis
  does to floats it assimilated, which is why the seventeen unassimilated buoys are printed
  separately.
- **Drift separation reaches the distance travelled by 30 days and overtakes it after**, 105 km
  against 108 km at 30 days and 212 against 165 at 90. A current field alone stops carrying
  information about a particular float quickly. Saying so is the feature.

---

## Not defects, and the reasons are worth keeping

- **`drift.ts` and `section.ts` duplicate science that also lives in Python.** Deliberate, and
  the only two. Held to the pipeline by `probe-drift.mjs` and `probe-section.mjs` - median
  0.331 km over 101 days, worst gap 5.07e-5 degC over 1,102 values. ADR 0015. **Do not add a
  third without the same harness.**
- **The bias map is not AI and has no confidence score.** It is the mean and RMS of residuals the
  bake already computed.
- **The upload is the only network call the frontend can make**, and only when a user drops a
  file.
- **The WOA climatology is a baseline and never a value.** Not in the Variable selector. ADR 0016.
- **The particle layer's share of the frame is a range, not a point** (1.83% and 2.47% on one
  unchanged build). The population is seeded with `Math.random()`; the probe asserts a floor.

---

## How to check any of this

The full command list is `CLAUDE.md`'s own Commands block. The short version, with a preview
server on 4173 and the API on 8000:

```bash
cd pipeline && ../.venv/Scripts/python -m pytest -q     # 409 tests
cd web && npm run typecheck && npx vite build
cd web && for p in landing guide tour controls hazard bias particles isolate                    outreach requirements drift section upload; do node probe-$p.mjs; done
```

`probe-section` and `probe-upload` need the API; the other thirteen do not. **All fifteen were
green on 2026-09-11**, along with 409 tests, pyflakes, the typecheck and the build: on a
baseline before any change, after Groups A and B, and on the finished tree after C, D and E.

**Run the API-needing two separately, and stop the API afterwards.** `probe-outreach` failed on
`page.goto("app.html?kiosk=1")` with a 60 s navigation timeout, twice in a row, while `uvicorn`
was up on 8000 - and **failed identically on a clean `HEAD` build**, which is how it was ruled out
as a regression rather than argued about. With the API stopped it passes first time. The server
holds the native Grids in memory and is competing with swiftshader for exactly the re-navigation
that rebuilds the whole scene, which is the shape of item 101. So the contention warning is not
only probe-against-probe: **a probe that does not need the API loses to one that is running.**

**And all thirteen can now go red.** Four of them - `requirements`, `controls`, `hazard`,
`isolate` - used to collect what they measured, print it and exit 0 regardless, which is why
"green" meant nothing for those four and why the two requirements links that opened the guided
tour survived a run that followed them both. They assert now: `probe-requirements` derives each
link's expectation from its own query string, `probe-controls` fails on its six rules,
`probe-hazard` fails on a leaked isosurface and on a colourbar that does not bend with the
shader, and `probe-isolate` reads the clip box back in degrees and compares it with the
Feature's own. The loop above is the complete list, and so is `CLAUDE.md`'s Commands block.
