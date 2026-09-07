# Known defects and open suspicions

**Worked through 2026-09-03, revisited four times on 2026-09-04 and again on 2026-09-06. Three items are open; 100 are
fixed.** The fixed ones are summarised rather than listed, which is this file's own convention: a
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
      the cast its own comparison was taken from, across all twelve analyses, because a residual
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
      palette buttons in a vertical list, each carrying a 46 px swatch. Re-measured at 1366x768:

      | Panel state | Content | Against a 636 px bay |
      | --- | --- | --- |
      | all groups closed | 377 px | fits |
      | Variable alone | 477 px | fits |
      | Variable + Colourbar | **780 px** | over by 144 |
      | Colourbar + Rendering | **806 px** | over by 170 |
      | bias | 918 px | over by 282 |
      | everything open | 2,115 px | over by 1,479 |

      **This is a regression with a name on it, not a mystery.** The switcher is a control the
      user asked for twice and it is not going away, but it has not been paid for out of the bay.
      A two-column grid of swatches, or putting the alternates behind their own fold, would get
      most of the 139 px back; neither has been tried. Nothing here needs a readout removed.

      The other lesson is the one this file exists for: **a fold figure written down goes stale
      silently.** Two documents carried "615 - exactly the height available" through a round in
      which it was already 25 px wrong, because a number in prose has nothing that can fail.

---

## Suspected, not confirmed

- **`coverage.py`'s band calibration may be measured against a bake that is gone.**
  `pipeline/samudra/coverage.py:80-84` says *"over 695,088 ocean voxels the median is 2 casts and
  the **maximum is 10**"*, and that the 1/2/4 bands split the block 19/23/36/22.
  `manifest.fields[coverage].range` is now `[0, 14]`, so the maximum has moved. **What could not
  be checked**: the split, which needs the twelve coverage Volumes decoded and de-quantised, and
  there is no native coverage Grid in `data/grids/` to do it from honestly. The argument the
  comment supports - that thresholds of 1/3/10 would leave the top band empty - survives either
  way, which is why this is not in the list above.

- **6 of the 25 rows in `provenance.html`'s test table say nothing.** `test_collocation.py`,
  `test_coverage.py`, `test_volume.py`, `test_argo.py`, `test_depth_warp.py` and `test_grid.py`
  have no module docstring, so `collect_tests.py:55` falls back to *"Covered by this module."*
  under a column headed *"What it defends"*. Confirmed as a fact; left here because whether a
  deliberate fallback printing an empty answer counts as a defect is a judgement rather than a
  measurement.

---

## Fixed, in summary

**100 defects across four rounds.** Every measurement that was worth keeping is now in one of
four places, which is why they are not repeated here: a rule in `CLAUDE.md`, a decision record in
`docs/adr/`, a probe that fails if it comes back, or a test.

| Round | What it was | Where the detail lives |
| --- | --- | --- |
| **2026-09-03**, 51 items | The September survey. The bias map pooling assimilated floats with unassimilated buoys; the drift score measured on days the current field does not cover; casts drawn on a section they were not in; a corridor measured against a rhumb line where the drawn line is a great circle; a masked corner refusing a whole column; render hints leaking between Fields; the log scale offered where it means nothing | ADRs 0015-0017, and the rules block in `CLAUDE.md` |
| **2026-09-04**, first pass, 12 items | The isosurface sharing the haze's coverage floor and putting sheets over India; current trails coloured by the value they sit on; a capture borrowing kiosk mode; volume controls hidden on a Field that draws a volume; `getBoundingClientRect()` on a hidden panel returning zeros | New rules in `CLAUDE.md`; `probe-hazard.mjs`, `probe-guide.mjs`, `probe-bias.mjs` |
| **2026-09-04**, second pass, 8 items | Two landing cards with alt text over an empty panel; a hero unreadable on light at 1.27:1; five hazard variables that all opened the same way; a heading claiming sixteen cards over fourteen; the deck two rounds stale | `probe-landing.mjs`, and three more rules in `CLAUDE.md` |
| **2026-09-04**, third pass, 8 items | Four folders holding overlapping copies of the same pictures; a publish silently replacing thirteen dark images with light ones; pictures that did not follow the theme toggle; `probe-upload.mjs` unable to run from a clone; the deck's numbers with nothing to check them against | `assets/screenshots/` as the single source; `pipeline/scripts/collect_facts.py` and `ppt/FACTS.md` |
| **2026-09-04**, fourth pass, 21 items | **The prose sweep.** `provenance.html` printing the superseded "currents are an image" line with `undefined m` in it; two requirements links labelled *Open a float comparison* that started the guided tour; the demo script reading numbers off the screen that the screen contradicts, and claiming all three variables share a worst 5-degree box; a landing tile pairing a median RMS with a mean absolute bias under a caption saying they were the same distribution; the retired 202-float drift score; 3,718 Argo casts that are 3,077; `longitude = 46` hardcoded on the page whose banner says nothing is; **four of the thirteen probes that could not go red**; `render-dossier.mjs` writing a PDF with three broken images | `CLAUDE.md`'s Commands block, the four probes' own assertions, and the rules below |

**Three of those are worth remembering as classes rather than as bugs**, because each came back
in a new costume: *a figure typed into prose cannot be checked by anything*; *a picture published
by a map with a hole in it fails silently*; and *"cosmetic" is a claim, so measure it before
believing it*.

---

## Things that look artificial and are not

Each has been queried once, and "that looks made up" is the correct first reaction to all of them.

- **The drift pin does not move and the line does not animate.** The line is the whole trip at
  once, and it starts at the date on screen, which is why scrubbing redraws it.
- **Markers move when the bias map is switched on, and there are more of them.** A residual
  belongs to the cast it was measured at, not to the date on screen. The map key says so.
- **The worst eight rows in the bias list share two colours.** The scale saturates at the ninetieth
  percentile (0.39 degC) and all eight are past it. The real gap is on the same row.
- **Hollow ringed markers** never measured that variable. Giving them the palette's midpoint would
  claim agreement with nothing.
- **A blank column in the vertical section** is land or sea floor, one grid cell wide because
  `Grid.column_at` refuses to blend across a Masked node. It is the data, not an artefact.
- **The deepest water in Temperature vs Normal is blank.** The atlas stops at 1500 m; the analysis
  runs to 2000 m. There is no normal to depart from.
- **Mean bias is almost exactly zero on all three Fields.** That is what an assimilating analysis
  does to floats it assimilated, which is why the nine unassimilated buoys are printed separately.
- **Drift separation reaches the distance travelled by 30 days**, 99 km against 103 km. A current
  field alone stops carrying information about a particular float quickly. Saying so is the feature.

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
cd pipeline && ../.venv/Scripts/python -m pytest -q     # 377 tests
cd web && npm run typecheck && npx vite build
cd web && for p in landing guide tour controls hazard bias particles isolate                    outreach requirements drift section upload; do node probe-$p.mjs; done
```

`probe-section` and `probe-upload` need the API; the other eleven do not. **All thirteen were
green on 2026-09-04**, along with 377 tests, the typecheck and the build.

**And all thirteen can now go red.** Four of them - `requirements`, `controls`, `hazard`,
`isolate` - used to collect what they measured, print it and exit 0 regardless, which is why
"green" meant nothing for those four and why the two requirements links that opened the guided
tour survived a run that followed them both. They assert now: `probe-requirements` derives each
link's expectation from its own query string, `probe-controls` fails on its six rules,
`probe-hazard` fails on a leaked isosurface and on a colourbar that does not bend with the
shader, and `probe-isolate` reads the clip box back in degrees and compares it with the
Feature's own. The loop above is the complete list, and so is `CLAUDE.md`'s Commands block.
