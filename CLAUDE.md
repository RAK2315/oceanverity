# Working on OceanVerity

Browser-native 3D ocean visualisation for INCOIS. Smart India Hackathon 2026, PS 26067.
Category Software, **theme Disaster Management**, team Sigmoid. The theme changed in the
September 2026 revision of the problem statement, along with four new dataset links. Every
one of those was tested on 2026-09-01 and the results are in
[`docs/plan/04-ps-update-2026-09.md`](docs/plan/04-ps-update-2026-09.md), which is the
current work plan. **Read it before starting anything.**

**Live:** https://rak2315.github.io/oceanverity/ (landing), `/app.html` (the platform),
`/provenance.html` (where every figure came from) and `/requirements.html` (every clause of the
PS against what answers it, with a link that opens the app on that control)
**Repo:** https://github.com/RAK2315/oceanverity - branch `main`, deploys on push

**Read [`CONTEXT.md`](CONTEXT.md) first.** It defines the domain vocabulary and the scope cut
line, and its terms - Grid, Volume, Profile, Collocation, Depth Warp, Source Adapter - are used
precisely throughout the code. Then skim [`docs/adr/`](docs/adr/): eighteen decision records, several
of which document traps that already cost hours. **0013, 0014 and 0017 are the September 2026
round**: currents became numbers and superseded 0011, five hazard Fields arrived with three new
ways of drawing a Field that is not a Volume, and the currents became *moving dots* without
becoming the volumetric streamlines this project has refused twice.

---

## What this thing is, in three sentences

It reads INCOIS's own gridded ocean analysis and the Argo float profiles measured in the same
water, renders the model as a GPU ray-marched 3D block you can fly into, and lets you click any
float to compare what it measured against what the model predicted, quantified. The demo runs
entirely from data baked into the build, so it makes zero network calls. A REST API exists for
the queries a static bundle cannot precompute.

---

## Where everything lives

### `pipeline/` - Python. Reads the data, does the science. All tested logic is here.

File-by-file map in [`pipeline/CLAUDE.md`](pipeline/CLAUDE.md), loaded when you work there.
The adapter seam is `oceanverity/sources/base.py`; the scientific truth is `oceanverity/grid.py`.

### `api/` - FastAPI. Answers what the static bundle cannot, and serves the open standards.

`api/main.py` is the REST half; `GRID_SOURCES` and `PROFILE_SOURCES` near the top are the
adapter registry. `api/standards.py` registers OPeNDAP, CF-1.8 NetCDF and OGC WMS, built on
`api/cf.py` (Grid to CF dataset), `api/dap.py` (DAP2) and `api/wms.py` (WMS 1.3.0). ADR 0012.
`api/upload.py` is the **only endpoint on the service that accepts anything**: a visitor's own
NetCDF file, as the raw body, parsed by `oceanverity/sources/netcdf.py` and held in memory for the
life of the process. Nothing is stored and the platform stays read-only.

**Every one of those reads the native Grid and none can reach a Volume.** This is the easiest
place in the project to break the first rule, because a consumer pulling NetCDF over the wire
cannot see that they have been handed a quantised, depth-warped picture of the data.

### `web/` - React + TypeScript + Three.js. One WebGL scene for globe and volume.

File-by-file map in [`web/CLAUDE.md`](web/CLAUDE.md), loaded when you work there.
The scene lives in `src/scene/OceanScene.ts`; every control is explained in `src/guide.ts`.

### Generated data - do not hand-edit

- `web/public/data/` - manifest, volumes (`.bin`), `surfaces/*.bin` (the hazard Fields, float32 on the Grid), `currents/vectors_*.bin` (float32 u and v on the Grid), **`grids/*.bin`** (the native float32 Grid for the three collocated Fields, which is what the vertical section is cut from), `floats.json`, `collocations.json`, **`residuals.json`** (the bias map), **`drift.json`** (the drift check), `anomalies.json`, **`tests.json`** (what the provenance page says about the test suite, written by `pipeline/scripts/collect_tests.py` rather than by the bake) and coastlines. Written by `bake.py`. 223 MB across 36 Timesteps.
- `web/public/fonts/` and `web/public/fonts.css` - the two typefaces, served from the build. Written by `scripts/fetch_fonts.py`. Do not replace with a Google Fonts link; that is the zero-network-calls rule.
- `data/grids/` - native Grids as `.npz` for the API. Server-side only.
- `data/woa/` - the World Ocean Atlas 2023 normal for this region, twelve months as `.npz`, 3.2 MB. Written by `pipeline/scripts/fetch_woa_normals.py` (and by any bake that had to fetch a month). Committed, because NOAA's OPeNDAP server was down on 2026-09-14 and 15. Server-side only.
- `data/glider/glider_prof_index_region.txt` - the 2,876 rows of the 248 MB EGO glider index that fall inside the region, cut from the real thing on 2026-09-01 with its own header kept. Committed so the glider finding is reproducible in every bake without the download. Server-side only.

### Documents

| File | What it is |
| --- | --- |
| `CONTEXT.md` | Domain vocabulary and the scope cut line. Read first. |
| `README.md` | **The submittable one.** Problem, what makes it different, the numbers, the architecture as text rather than only a picture, how to run it. Kept short on purpose; anything that wants a page of its own goes in `docs/`. |
| `docs/README-full.md` | The long-form README this replaced: every PS clause answered, every variable explained, the full requirement audit. Nothing was deleted, only moved. |
| `docs/adr/00*.md` | Eighteen decision records. **0018 is the newest**: chlorophyll, oxygen, the oxygen floor and surface fronts, never called a fishing zone. Before it, 0017: the flow drawn as moving dots, which is the drift model's own integrator and is *not* the volumetric streamlines this project still refuses. Before it, 0015 (drift that publishes its own score) and 0016 (a real 1991-2020 climatological baseline). |
| `docs/OceanVerity-Dossier.pdf` | Full project dossier including an anticipated-questions section. Regenerate with `web/render-dossier.mjs` from `scripts/dossier.html`. |
| `docs/demo/script.md` | The demo script: what to say, what to do. |
| `docs/plan/00-data-sources-verified.md` | Every endpoint tested, including the dead ones. |
| `docs/plan/01-cut-features.md` | What was cut, what is worth adding back, known rough edges. |
| `docs/plan/03-requirement-gaps.md` | Every unmet clause of PS 26067, researched with dates and row counts, and the decision taken on each. Read before proposing to add a data source. |
| `docs/plan/05-coverage-audit-and-ideas.md` | The PS audited clause by clause against what answers it, and the ideas that close what does not. Names the four operational mandates the PS lists, and the outreach section it answers with one tour. **Partly out of date**: it calls fishery advisories the one unanswered mandate, and ADR 0018 answered it on 2026-09-15. |
| `docs/plan/07-incois-services-and-what-to-build.md` | **A discussion document, nothing agreed.** INCOIS's own ~20 operational services, which of them this platform already has a counterpart for (cyclone heat potential, SARAT, the PFZ ingredients), and four build candidates with the honest cost of each - every one needs a bake, which invalidates screenshots. Read off the owner's screenshots of incois.gov.in on 2026-09-21 and **not re-verified against the live site**. |
| `ppt/README.md` | **The deck folder's index**: the sixteen screenshots and what each is for. **Only screenshots go on a slide** - the nine "infographic boards" were pictures of text and are deleted; `DECK.md` carries their content as words to be typed natively. |
| `ppt/DECK.md` | The content for each of the six slides, and a prompt for the two things that are genuinely diagrams. |
| `ppt/NOTES.md` | **What actually gets a deck shortlisted**, in one page: a judge spends 3-5 minutes, the five things that get decks rejected, and what to resist on this project - the rendering is the least important thing about it. |
| `ppt/script.md` | **The prototype video, version 2** (2026-09-20), 4:30-5:30, narration beside the exact screen actions. Must tell the same story as `DECK.md` in the same order, and speaks no count that moves with a bake. `ppt/script-v1-recorded.md` is what the video already recorded says, locked and partly wrong. Distinct from `docs/demo/script.md`, which is the live deck-plus-demo talk. |
| `ppt/FACTS.md` | **Generated.** Every figure the deck may quote, read off the bake by `pipeline/scripts/collect_facts.py`. `DECK.md` has warned "do not adjust a number by arithmetic" for three rounds; this is what that warning points at. |
| `assets/screenshots/{light,dark}/` | **The one copy of every screenshot**, named by what it shows. `docs/images/`, `web/public/images/` and `ppt/images/` are outputs, filled by `cd web && node capture.mjs --publish-only --publish`. |
| `design/STITCH.md` | Per-screen prompts for Google Stitch. |

---

## Commands

```bash
# tests - run before claiming anything works
cd pipeline && ../.venv/Scripts/python -m pytest -q

# refresh the manifest's palette tables from oceanverity/palettes.py, without a full bake
cd pipeline && ../.venv/Scripts/python scripts/refresh_palettes.py

# refresh the manifest's Field label, units and description from the FieldSpecs in bake.py.
# Prose only; every measured key is left to the bake that took it. Run it after editing one.
cd pipeline && ../.venv/Scripts/python scripts/refresh_field_prose.py

# where a figure is typed wrong in a document, against the build. Read docs/NUMBERS.md first.
cd pipeline && ../.venv/Scripts/python scripts/check_figures.py

# what the provenance page says about the tests. Run it after adding or removing any.
cd pipeline && ../.venv/Scripts/python scripts/collect_tests.py

# typecheck and build
cd web && npm run typecheck && npx vite build

# refresh the data from INCOIS and Argo. 36 steps, about 36 minutes, and it CLEARS volumes/,
# currents/, surfaces/, grids/ and data/grids/*.npz before writing - so a smaller --timesteps
# replaces the committed bake rather than sitting beside it. Read the memory note further down.
cd pipeline && ../.venv/Scripts/python -m oceanverity.bake

# run
cd web && npm run dev                                     # http://localhost:5173
.venv/Scripts/python -m uvicorn api.main:app --port 8000  # the REST API

# regenerate artefacts
cd web && node render-diagrams.mjs      # the README's architecture diagram, from scripts/ppt_diagrams.html
cd web && node render-dossier.mjs       # the dossier PDF
cd web && node capture.mjs --theme light --publish  # screenshots: shoot, encode as JPEG, copy into the docs
cd web && node probe-hazard.mjs         # measures the sheet, the drape and the arrows
cd web && node probe-guide.mjs          # every control has an entry, every figure in one is live
cd web && node probe-controls.mjs       # every Field against its log and isosurface controls
cd web && node probe-isolate.mjs        # the anomaly clip lands on the feature it points at
cd web && node probe-bias.mjs           # the bias map: every marker's tint against palette.ts
cd web && node probe-drift.mjs          # the browser's drift integrator against the pipeline's
cd web && node probe-particles.mjs      # the moving flow: it is the drift model, it draws, no dot on land
cd web && node probe-tour.mjs           # "Show me around" visits every control, and survives
cd web && node probe-outreach.mjs       # every Explore question keeps its promise; kiosk; the copied link
cd web && node probe-palette.mjs        # the colourbar switcher: right alternates, water and legend agree
cd web && node probe-chrome.mjs         # every text role in the console chrome, both themes
cd web && node probe-landing.mjs        # the landing page: no missing picture, an honest count, a readable hero
cd web && node probe-requirements.mjs   # every figure filled, every deep link lands on what it promised
cd web && node probe-case.mjs           # the Montha walkthrough: each step, each figure from montha.json, the track
cd web && node probe-section.mjs        # the browser's section against /api/section   (needs the API)
cd web && node probe-upload.mjs         # drop a NetCDF in, and refuse one              (needs the API)
```

Deployment is automatic: push to `main` and the GitHub Actions workflow builds and publishes.

---

## Rules that matter here

**A publish is a total, silent overwrite, so the map decides the theme and not the operator.**
`capture.mjs --publish --target site` with a *light* `shots/` directory replaced thirteen dark
pictures with thirteen light ones in under a second, on a landing page that is dark by default,
and printed thirteen cheerful `published` lines while it did it. It was recoverable only because
`web/dist/images/` still held the previous build's copy of `public/` - luck, not design, and the
six tracked files in git were from an August commit rather than the round being worked on.
So `WANTS_THEME` now names what each document's pictures are supposed to be - `docs` and `ppt`
light, `site` dark - the run stamps `shots/.theme` **before its first shot**, and a mismatch is
refused per file rather than warned about. The rule needed a **per-entry override** almost
immediately: the exhibition screen is dark in all three documents, so a light `--target ppt`
run passed the per-document check and quietly replaced it. **Two entries writing one file is the
same failure one level up** - `08-coverage` and `handpicked/coverage` both named
`web/public/images/coverage.jpg`, and the winner was whichever came later in the list.

**There is one home for every screenshot, and the three image folders are outputs.**
`assets/screenshots/light/` and `assets/screenshots/dark/` hold one copy of each picture, named
by what it *shows* - `collocation`, `hazard`, `bias` - not by which document uses it, because the
same frame is `hero.jpg` in the README, `volume.jpg` on the landing page and `S2-app.jpg` in the
deck. `docs/images/`, `web/public/images/` and `ppt/images/` are filled from there by
`node capture.mjs --publish-only --publish`, which opens no browser and takes about a second.
Four folders holding overlapping near-copies in two themes is how a project stops being able to
say which picture is current, and that lasted a round here: one of the sets was from August and
nothing pointed it out.

**`web/shots/` is scratch and a capture may not promote itself.** The next run overwrites
`shots/` wholesale, so nothing may reference it. `--ingest` is what copies a shot into
`assets/screenshots/`, it is **opt-in**, and it refuses to overwrite anything in `HANDPICKED`
without `--force` - because the harness shoots one camera angle per state and cannot tell that
its own flow shot has no Somali Current in it. Most of the eighteen light pictures were
grabbed from a real browser for exactly that reason. `scripts/normalise_screenshot.py` crops a
grab to 16:9 and resizes it to the harness's own 1600x900 at quality 82 - **crop and resize
only**, because a screenshot is the deck's proof and may not be retouched. `--no-crop` exists for one real case: a frame wider than 16:9 whose
subject is on the right, where cropping left keeps the panel and throws the subject away.

**A publish map with a hole in it is invisible everywhere except on the page.** `PUBLISH_MAP` in
`capture.mjs` sent `07-anomaly` into `docs/images/` and not into `web/public/images/`, and two
cards on the landing page asked for `./images/anomaly.jpg` and got alt text over an empty panel.
Nothing could catch it: no build compiles HTML against the files it names, no typecheck sees an
`<img src>`, and every other probe drives `app.html`. `probe-landing.mjs` now checks both copies
- the file in `web/public/images/`, which is what a publish writes, and a non-zero `naturalWidth`
in the browser for what the preview serves out of `web/dist/`, because a publish that never made
it into a build fails only the second. It also fails on an external request, on a heading whose
number word disagrees with the number of cards under it, and on hero type that drops under 3:1
against the ground actually under it.

**The hero is a dark band in both themes, and it carries its own colours to be one.** The
photograph stays the same dark render on light, deliberately - a light capture of ray-marched
water is a worse picture. The *type* followed the page, so on light `--ink` is `#0d1b22` and
"Fly into the" was near-black over the darkest part of the image. Measured against the rendered
ground beneath it: the headline was **3.66:1** at 1600 px and **3.97:1** at 1280, and the cyan
"Indian Ocean." was **1.27:1**, which is no contrast at all. Neither scrim could fix it, because
the problem was the ink and not the ground. `.hero` re-declares the dark palette for everything
inside it and keeps its scrim dark to its own bottom edge - it used to fade to `var(--deep)`,
which on light is nearly white and would have put light ink and dark tiles on a pale ground.
Measured after: headline **6.49** and **6.15**, accent **3.46** and **3.50**, and **light and
dark now agree to two decimal places at both widths**, which is the check that the band is one
band. `probe-landing.mjs` fails if they ever separate.

**Four variables that are all "a depth to do with warm water" have to say why you would open
this one.** Cyclone Heat Potential, Depth of 26 degC, Mixed Layer Depth, Isothermal Layer Depth
and Barrier Layer Thickness read one after another in the same panel, and every entry opened with
its own definition and none with its neighbour. They are one chain - how much fuel there is, how
far down it reaches, how far the wind has stirred, that same boundary measured with a thermometer
instead, and the gap between the last two - so **the first bullet of each now names its neighbour
and says what it asks instead**. Nothing measured was cut to make room: barrier layer's level
spacing moved from `means` into `look`, which is where a limitation of the picture belongs.
Measured by `probe-guide.mjs`: median **118 words** on the panel, unmoved; longest 151; no list
over 4 bullets; longest bullet 20 words against a limit of 24.

**A surface asserts a position; haze does not, and they cannot share a coverage floor.** The ray
marcher draws water wherever coverage is above 0.02, which is right for the haze: it fades, and
nobody reads a position off it. The isosurface used the same floor, and an isosurface says "the
value is exactly this, **here**" - so near the coast it kept drawing for almost a full cell past
the real shoreline, out of the neighbouring cell's back-filled value. That is what put sheets
over India and Sri Lanka. It now needs `coverage > 0.6`, ramped to 0.9 so the cut is not a second
staircase. Measured: **16.5% of ocean voxels touch land horizontally**, which is the shell this
acts in; on screen the surface went from **23.20%** of the frame to **22.86%**, and an extreme
floor of 0.97 only reaches 22.60% - so the whole borrowed-value fringe is about 0.6 points of the
frame. **Small in area, conspicuous in position**, which is why area was the wrong thing to
optimise and the coastline was the right thing to look at.

**The exhibition screen restores the operator's camera before every question, and never zooms.**
`focusOn` hard-sets the camera to a fixed radius and `panTo` preserves whatever distance it finds,
so the one question that zoomed to a float left **every later question** framed at float distance,
for the rest of the day. Measured: `focusOn` took the camera from **79.9 units to 22.1**, and the
next `panTo` inherited 22.1. Two halves to the fix - kiosk remembers the pose it opened on and
puts it back before each question, and the loop is handed a `focusOn` that pans - so a question
can neither take the framing away nor leak a distance forward. Measured after: 79.9 held across
all six questions, worst change **0.0 units**. Restoring between questions is safe because the
loop is already paused while anybody is touching the screen. Explore keeps the zoom, because there
a reader pressed the question and the comparison panel is on screen to read.

**Kiosk mode is not a CSS state, so nothing may borrow it for a screenshot.** `capture.mjs` hid
the panels for its hero shot by turning kiosk on, which also mounts the component that plays the
nine Explore questions on a loop - so the hero came back as the *currents*, with a drift pin in
it, because two questions had run while the frame was being taken. Bare shots inject a
stylesheet and touch nothing else.

**No backticks inside a GLSL template literal.** A comment written with `pipeline/oceanverity/
volume.py` in backticks ended the string, and TypeScript reported it as a missing comma two lines
later. The shaders are template literals; markdown habits do not survive in them.

**A mark drawn on top of a field coloured by the same number is invisible, and that is
structural rather than aesthetic.** The current trails took their colour from the palette, like
the arrows - and they sit directly on water coloured by the same speed through the same palette,
so over slow water a pale dot lands on pale water and has zero contrast against exactly the
background it is drawn on. Most of the basin, on both themes. The trails are **inked** now, one
colour per theme, and carry direction only; speed is still carried by the water underneath, by
how far a dot travels per frame, and by the number under the cursor. This is the **one** mark in
the platform not coloured by its own value, so it is the one place the legend has to say so - the
map key names the trails as flow and the water as speed. Measured: the layer went from **1.33%**
of the frame to **1.83%**. The Transfer Function window still drops a dot outside it rather than
inking it, so narrowing the range stays analytical.

**That share is a range and it was written down as a point.** `particles.ts` seeds its 2,400
dots with `Math.random()`, so where they happen to be when a probe takes its frame is not the
same twice - measured **1.83%** on 2026-09-04 and **2.47%** on a re-run the same evening, on an
unchanged build. **And the probe's printed share is no longer the on-water share at all**: since
2026-09-23 it takes its frame pair with the water switched off, so the figure it prints (2.0 to
2.6% over four runs) is the layer over bare ground. Quote the probe for "does it draw", never
for "how much of the screen is it". `probe-particles.mjs` was always right about this: it
asserts a *floor* and that
the layer beats its own hidden baseline threefold, not an exact figure. Anything quoting the
share has to quote both ends, and **the pre-ink 1.33% is one sample of the old layer against one
sample of the new one**, so it sizes the change loosely and not to two decimal places. If a
precise figure is ever needed, seed the population deterministically for the probe rather than
re-running until a number looks familiar.

**A Field can be two render kinds at once, and `render` names only one of them.** Current Speed
declares `render: "vector"` and *also* carries a Volume, and `OceanScene` hides the volume mesh
only for a sheet or a drape - so the currents drew a block of water while `Controls.tsx` hid Water
opacity, Ray steps and Show volume, all three gated on `render === "volume"`. A reader was shown a
layer with no control over it, which is the "hiding a control is not turning it off" rule running
the other way: the *thing* stayed on while its control was hidden. **A panel predicate about what
is drawn has to be the scene's predicate**, and the scene's is `isSurfaceField` - not a sheet, not
a drape.

**A pretty layer gets the measured integrator, not a cheap one.** The current flow is a few
thousand dots carried by the field, and nobody reads a number off it - which is exactly the
argument that would have given it its own advection code. It runs `midpointStep` and `sample` in
`drift.ts` instead, the two functions the scored drift model runs on, and `integrateDrift` was
refactored onto the same step in the same change so there is one copy and not two. Measured by
`probe-particles.mjs`: a particle and a drift pin from the same start point over the same elapsed
ocean time end **0.002 km apart after 724 km of travel**. That equivalence is the entire claim -
an animation whose error is published, median 41.0 km over an Argo cycle - and an unchecked claim
is decoration. ADR 0017.

**A dot on a Level is not a streamline through the block, and the difference is `w`.**
`CONTEXT.md` and `README.md` both said particle advection was "a project in itself", which was
true of the three-dimensional version and read as a refusal of both. Copernicus publish `uo` and
`vo` and no vertical velocity, and INCOIS publish neither, so a 3-D particle claims a motion
nobody measured. A sheet of dots on the chosen Level claims nothing beyond the two components
that exist. **And do not bake a finer field to make it prettier**: 1/12 degree over this region is
about 2.2 MB a Timestep and would be affordable, and it would make the picture finer than every
number the platform reports.

**Changing a default silently retires the probe that measured the old one.** The current layer's
default became moving dots, and `probe-hazard.mjs` went on printing `arrowVertices: 0` and a
`share` of 3.33% that was the animation moving between its two frames rather than the arrows being
drawn. It passed, because it printed those numbers and asserted on neither. It now sets
`currentStyle: "arrows"` before measuring arrows, hides **both** styles for the off-frame, and
fails on a vector Field that builds no arrow geometry. Correctly paired the arrows are **0.59%**
of the frame, which is the figure this file has quoted all along.

**A probe that collects, prints and exits 0 is a log, not a check - and it reads as green.** Four
of the thirteen had no `process.exit`, no `exitCode`, no `throw` and no assertion of any kind, so
they passed whatever they measured. They were not quiet about it: `probe-controls.mjs` built a
`broken` array against six rules and only logged it; `probe-requirements.mjs` followed all 21 deep
links, printed the state each one landed in, and never compared it with the `href` - which is why
two links labelled **"Open a float comparison"** pointed at `?dive=1&tour=1` and started the
guided tour instead, through a run that followed both. `probe-hazard.mjs`'s scale check read
`.colourbar` with the Colourbar group **shut**, got `null` every time, and printed
`"barStops": null` under a heading claiming to check that the water and the legend bend together.
`probe-isolate.mjs` wrote two frames to `shots/` and compared neither. All four assert now, and
two of the four needed the *measurement* rethinking rather than an `exit` bolted on: the isolate
diff was 83% Anomaly-panel fade-in until it was bounded to the band between the panels, and a
pixel test could never have caught the mirrored clip anyway - the camera compresses 35 degrees of
latitude into about 3 px a degree, so the 8-degree bug moves the water 27 px. It reads the clip
box back **in degrees** instead. **Before adding a probe, make it fail on purpose once.**

**"Show me around" walks every control, and that is a measurement.** It was five steps against
every control the guide explains - a demo, not a tour, and the four the user's teammates would
present from were among the ones it never visited. It is 23 steps in 6 chapters now, and every
step declares the `GUIDE` keys it puts on screen. `probe-tour.mjs` fails if any entry in `GUIDE`
is not named by some step, if a step ends the tour, or if a step changes nothing the scene
reads. **Add a control, give it a guide entry as the rules already require, and the probe tells
you the tour has stopped being complete.**

**A touch pauses a tour or walkthrough; it does not close it.** Closing lost the reader's place:
one slider tried mid-tour, and the tour was gone (owner report, 2026-09-15). `set("touched")` and
`hazardPreset()` now set `cardPaused` instead of nulling `tourStep` and `caseStep`. The card
stays with **Continue**, which re-applies that step, and **End**. Nothing moves the scene while
paused, and any change of step clears the pause.

**A step that presses a control on the user's behalf has to clear the pause itself.** The tour's
and the walkthrough's effects re-assert the index and clear `cardPaused` after every step for
exactly that reason. This is why every step drives `setState` directly and never `set`.
`probe-tour.mjs` and `probe-case.mjs` check the pause, Continue and End.

**The outreach half lives behind one door, and the console gains nothing.** Six scattered buttons
would have been the easy version and it would have left the product with no front door at all.
`Explore` is one full-screen surface holding all nine questions, the float journey, the coverage
view and true scale; `?kiosk=1` is the same list with the panels hidden, the type scaled and a
reset a minute after the last visitor walks away. **The left panel gained zero groups.**

**Every simplified question carries its caveat, beside it and never after it.** "Where could a
cyclone get stronger" is a map of conditions and not a forecast, and the reader this door exists
for is exactly the reader who will not make that distinction unprompted. `probe-outreach.mjs`
fails if one of the five questions that simplify a limit away has no `caution`, and it checks each
question against what its own card promised rather than against "it did something".

**`getBoundingClientRect()` on a `display: none` element returns zeros, and zero is a number.**
The depth ruler places its figures beside the control panel by measuring it. In kiosk mode the
panel is hidden, so the measurement succeeded, returned 0, and every landmark ran off the left
edge of the exhibition screen. Presence is not the question; width is.

**`scrollbar-gutter: stable` is asymmetric by definition.** It reserves the track on the scrolling
edge only, so the panel's contents sat 1 px from its left edge and 11 px from its right,
permanently, on the panel a judge looks at first. `both-edges` fixes it and - measured at
1366x768, both ways, three open sets - **costs no height at all**: 408 px closed, 527 px with
Variable open, 722 px with Variable and Colourbar, identical under either value. What it costs is
11 px of content width, which nothing in the panel needed.

**A tab that folds a bay the reader cannot see is not a control.** `BayToggle` mounted
unconditionally, and on the globe nothing is in the right bay until a control is touched - so the
right tab docked to an edge that was not there: measured at 1400x800, a 22x34 square at 1030,61
beside the cue card's 320x149 box at 1062,88, detached by 32 px and sitting 27 px above it. It
reads as that card's close button and it half is one, because the fold rule covers `.cue` as
well. A tab is drawn now only where its bay holds a panel, and the question there is **presence,
not width**: a folded panel is `display: none` and measures zero, which is exactly the state the
tab exists to undo. That is the `getBoundingClientRect()` rule two paragraphs up, read the other
way round, and which of the two you want depends on what you are asking.

**Two pieces of state that each draw a card have to be made exclusive in one place.** `tourStep`
and `caseStep` are independent, both render at the foot of the screen, and six places opened one
of them while only three closed the other - so Explore, Cyclone Montha, then "Show me around"
stacked two cards **21 px apart** with the second reading out from behind the first, and left
IMD's storm track on the water under a tour that explains no such thing. Owner report,
2026-09-24. `startTour()` and `startWalkthrough()` are the rule, and every opener including the
deep link goes through them. **The track goes with its walkthrough**, deliberately: `MapKey`
names it under exactly the condition that draws it, so a track outliving the flow that drew it
would be an unnamed mark on the water.

**A band you clear is cleared in both axes, or the thing clearing it follows the band around.**
`DepthRuler`'s caption keeps above the time axis and the map key by reading their top edges every
frame, which is right for a fixed band along the foot and wrong for a legend the reader can drag.
Measured at 1400x800: the key dragged from y 570 to y 214 took the caption from y 547 to **y
215**, and parking the key in the top right corner - out of the caption's column entirely, with
nothing in its way - still pulled the caption to **y 30**. A band is in the way only where it
overlaps the caption's column *and* reaches down to where the caption is going, and the bands are
folded lowest-first, because clearing the time axis can otherwise walk the caption into a key
parked just above it. What did not change: where the column's foot runs past the time axis the
caption is pushed into the figures and overlaps one - *300 m* by 14 px of box before, *2000 m* by
8 px now.

**Two modules are deliberately implemented twice, and both copies are measured against each
other.** The standing rule is one curve in one file - `transfer.ts` exists because a second copy
of the Scale silently disagreed with the first. Drift and the vertical section break it once
each, because both are interactive and both have to run where the user is: the demo runs with
the API off and the static deployment at `rak2315.github.io` has no API at all, so an API-only
version would be dead on stage and dead on the link a judge opens. The rule is kept the only way
that survives: `web/probe-drift.mjs` and `web/probe-section.mjs` run the **shipped browser
modules** against the pipeline's and fail on disagreement. Measured - drift, median 0.331 km and
worst 1.573 km over 101 days; section, 1,102 values with a worst gap of 5.07e-5 degC. Do not add
a third without the same harness.

**A deleted CSS class is a silent regression, because nothing compiles CSS against its markup.**
`GuidePanel` moved from three prose blocks to bullets a round ago and `.guide-body` went with
them - but `AnomalyPanel.tsx` still uses the class, so the Anomaly Feature panel quietly reverted
to a browser-default definition list: label flush left, value indented under it, no rule, no
spacing. No error, no missing element, nothing a typecheck or a probe was looking at. When a
class is removed, grep the whole of `src/` for it before deleting the rules.

**A figure on the guide panel comes from the bake, never from the sentence around it.**
An entry writes `{token}` and `guideFigures()` fills it from the manifest; a token with nothing
behind it takes its whole bullet off the panel, because a sentence that cannot be completed
truthfully is better absent than approximate. Four figures were typed in by hand and every one
moves on a re-bake - the anomaly-feature counts had been stale since August and nothing could
notice, because a wrong number and a right number are the same shape. `probe-guide.mjs` fails on
an unfilled token reaching the screen, and on a control with no entry at all: it found three,
which is the rule two paragraphs down being broken silently for a round.

**INCOIS's gridded Argo analysis is built from these floats, so a float's residual is largely
the analysis agreeing with data it was made from.** The seventeen moored buoys are not described
as inputs to that analysis, which makes them the closer thing to an independent check. Do not
write "INCOIS assimilate": the VAM analysis is gridding, not data assimilation into a model, and
whether it excludes buoys is unverified (INCOIS-GODAS, a different product, does assimilate RAMA
and NIOT moorings; `docs/plan/06`, 2026-09-15). Measured on 2026-09-23 they disagree **4.8x**
more on temperature - 0.884 degC against 0.184 - **7.8x** on salinity and **6.8x** on density.
Pooled into one basin-wide number the seventeen of them vanish into 246 floats and the headline
becomes a statement about self-consistency. At twelve Timesteps it was nine buoys at 4.5x; a
full year roughly doubled the evidence and the buoys still disagree more on all three Fields.
**Read the three ratios off `residuals.json`'s `byKind` blocks and never from this paragraph**:
they said 5.5x, 7.7x and 5.4x for a round after the bake moved - here, in `residuals.py`'s own
docstring, which named the 36-step bake while quoting the twelve-step one, and in
`docs/plan/02`. `residuals.field_bias` takes a `kind` and the panel prints both. Any new
sentence about "how far the model sits from the observations" has to say which observations.

**A score may only be measured on the days the data covers.** `CurrentSeries._bracket_time`
holds the first analysis rather than extrapolating before it, which is right for drawing a line
and silent inside a number. Measured at twelve Timesteps: the earliest Fix was 2026-03-22 against
a first analysis of 2026-04-10, and 199 of 202 baked drift comparisons started inside that 19-day
hole. `CurrentSeries.covers` refuses them - the same refusal `choose_cast` and the Float markers
already make - and the score moved from 39 km to 38 km over one cycle, on 195 floats rather than
202. The window is a year now and the score is 41 km over 6,185 cycles on 217 floats.
**Anything drawn is separate from anything scored**, and the browser's integrator is unchanged:
a dropped pin always starts inside the window.

**A cast drawn on a figure is an observation of the water in that figure, or it is a lie.**
The vertical section took every fix of every float in the corridor with no time filter at all:
measured on a line from 80 E, 5 N to 90 E, 20 N at the last Timestep, 127 casts drawn and 98 of
them from March to June, under a caption saying "casts within 150 km of the line". It now uses
the bake's own coverage window, which is the rule `floatTime.positionAt` already enforces for the
markers - 8 casts on that line, all from July.

**A corridor is measured against the line that is drawn, and the line drawn is a great circle.**
`casts_near_line` projected onto a straight line in degrees scaled by the cosine of the mean
latitude, which is right at the middle of a section and wrong at both ends, and is a rhumb line
rather than the great circle `section_along` samples. Measured against a numeric minimisation
over 20,001 points of the drawn line, on 45 E 10 S to 100 E 25 N: the reported offset was out by
up to **179 km** against a corridor 150 km wide. Both copies now use the spherical cross-track
and along-track pair, which has no length at which it stops being right.

**A masked corner refuses a Level, not a column.** `Grid.column_at` makes one Level missing when
one of its four corners is; the browser's first section refused the **whole column** instead, so
every place where the sea floor cuts in blanked the good water above it - 142 of 1,464 cells in
one Bay of Bengal cut, all of them water the model has. The values were correct to 5e-5 the
whole time, which is exactly why "the numbers match" is not the same question as "the picture is
right".

**Never answer a scientific question from the `Volume`.** It is quantised to bytes,
depth-warped and back-filled across land for the GPU's benefit. Collocations, tooltips, API
responses and anything a user reads as a measurement come from the `Grid`. This is why
`data/grids/` exists.

**Do not re-derive the Depth Warp.** The pipeline ships the sampled axis in the manifest
(`depthAxisMetres`) and the frontend inverts it via `geography.ts`. A second copy of the formula
drifts silently. This has already been fixed once.

**The bias map is a composite, and the timeline says so where the confusion happens.** Every
instrument is drawn at the cast its comparison was taken from, across all thirty-six analyses - a
residual measured at one position on one date is a number on the wrong water anywhere else. So
pressing play animates the field and moves **no marker**, which reads as a broken animation. The
map key said this already and the map key **folds, and is remembered folded**. The time axis now
says it too, in `--secondary`, whenever the mode is on: a caveat belongs on the band whose button
was just pressed, not two panels away behind a disclosure someone shut last week. **And
switching the mode on moves the timeline to the newest analysis**, through `store.setBiasMode`,
which the checkbox, the tour and Explore all call. Pressed at 30 Dec 2025 the 199 markers on screen
moved a median 258 km and 52 more appeared, because 206 of 251 comparisons were taken at the last
two steps - reported as a bug. At the newest analysis 92% of them do not move at all, so the press
reads as the dots changing colour. The markers are still pinned to their casts; only the date the
mode opens on changed.

**A frame pair must differ by exactly one thing, and neither a store change nor a fixed wait is
ever that thing.** `updateArrows` and `updateSheet` set their mesh's `visible` back to true on
every `push(state)`, so a probe that changes the store between the "geometry on" frame and the
"geometry off" frame gets two identical frames and reports that the Field draws nothing.

**The second half of that rule cost two reproducible failures on 2026-09-23.**
`probe-particles.mjs` waited 500 ms between its frames and called the difference a baseline for
background motion - and the ray marcher's `uTime` moves **3.16%** of the frame in 500 ms, against
a whole dot layer of 2.7%, so its control was bigger than its signal and the check could not
pass. Switching the volume off for the pair took the baseline to **0.000%**, which proved the
water was all of it. Then it failed again, one run in two, with the baseline at 2.67%: **500 ms
is not reliably longer than one swiftshader frame**, so the screenshot after the hide sometimes
still held the layer that had just been hidden, and the control became the signal. Wait on two
`requestAnimationFrame`s, never on a duration, and switch off anything that animates **before**
the pair rather than between its frames. It happened: the current
arrows were measured as hidden under the water at 0.007% of the frame, and correctly paired they
are 0.54% with the water on against 0.59% with it off - not hidden at all. The render loop is
continuous, so moving `visible` alone is enough. **And never diff PNG bytes for a magnitude**:
compressed bytes shift wholesale from a handful of changed pixels, which is why the same frames
read as "99.4% different" and as "0.5% different" depending only on which was counted.

**A world position is not a clickable pixel, because the two bays sit over the glass.** The new
cursor check in `probe-hazard.mjs` projected the fastest water in the block to canvas
coordinates and moved a real mouse there - and the fastest water in this basin is the Somali
Current at about **51.5 E**, which is behind the left panel. The move landed on the panel,
`onCanvasMove` never fired, and the probe correctly reported that the scene answers
**2.937 m/s** while the store holds `null`. That reads as a broken readout and is a probe aiming
at a covered pixel. Ask `document.elementFromPoint` what is on top before driving a real pointer
at a projected position; `scene.pickCurrent` answers for covered pixels quite happily, which is
exactly why the two halves of that check fail for different reasons and both are worth making.

**Verify rendering by measuring, not by looking.** The worst bugs here all looked like shader
bugs and were not: invisible deep water, a "thin sliver" volume, a half-cell field offset,
frozen floats. `OceanScene.debug()` reports the real transform, uniforms and projected screen
extent. `window.__scene` and `window.__store` are exposed for this. Screenshot with
`web/capture.mjs`; measure pixel extents in Python when the eye is not enough.

**Transparent draw order is explicit.** See ADR 0006. Three.js sorts by centroid, meaningless
for world-spanning geometry. Anything new and transparent needs a `renderOrder` from the `ORDER`
table in `OceanScene.ts`.

**A remembered key has six copies, and two of them are harnesses.** The project was renamed
OceanVerity on 2026-09-20 and the four `localStorage` keys moved to an `oceanverity.` prefix.
`web/src/remembered.ts` is the one module the app reads and writes them through, and it falls
back to the old prefix once so a returning reader keeps their theme and their folds. But the
three static pages each carry an inline twin, because they set `data-theme` before first paint
and cannot wait for a module - and `capture.mjs` and `probe-landing.mjs` write the theme key
**directly**, to force a theme. Leave those two behind at a rename and they set a key nothing
reads, every page falls back to dark, and a `--theme light --publish` run writes dark pictures
into the light targets while printing cheerful `published` lines. That is the silent-overwrite
rule with a new way in. Verified after the move: all four pages read the old key, apply light,
write the new key and drop the old one.

**The rename is finished, package included.** `pipeline/oceanverity/` was the last piece and
landed on 2026-09-21, a day after the rest: 84 files, every import, every
`python -m oceanverity.bake`, and - the one that would have been silent - the `HISTORY` path list
in `check_figures.py`, which classifies a stale figure by the directory it sits in and would have
started reporting the entire pipeline as CURRENT if it had kept pointing at the old name.
**The only `samudra` left in the repo is the legacy `localStorage` fallback** in
`web/src/remembered.ts` and its three inline twins, which exist so a returning visitor keeps the
theme they chose. A grep for anything else should return nothing.

**The demo path makes zero network calls.** Everything the browser needs is in
`web/public/data` and `web/public/fonts`. Keep it that way; a dead venue network must not be
able to kill a demo. This was quietly false for a while - all three pages linked Google Fonts,
about 63 KB over three requests - while the README carried a badge saying otherwise.

**If you add a control, add its guide entry.** An unexplained control is worse than no control.
`src/guide.ts` is the single place. A Field with a `GUIDE` entry under its own key explains
itself when clicked; the rest fall back to the entry for the selector.

**The left panel says what and how much. The guide panel says why, in points.** Both used to do
both and neither well: the panel carried a paragraph restating what the guide already said, and
the guide answered in three prose blocks of 40 to 70 words that nobody reads while a demo is
running. A `GuideEntry` is now one sentence of definition plus `means` and `look` as **bullets,
max 4, max 2 lines each** - about 70 words against 170. **Every number keeps its unit and
survives; only words get cut.** A sentence on the left that explains rather than reports belongs
on the right, and a figure on the right that is already a readout on the left belongs on the
left.

**Colour last. Bilinear on the values, never on the colours.** The Sheet and the Drape sit on a
56 x 36 Grid - about 110 km a cell - and read as tiling under a full-resolution coastline.
`src/surface.ts` upsamples the lattice 4x *before* anything is coloured, because halfway between
two ends of a diverging palette is its pale midpoint: blurring colours across a warm patch and a
cool one would draw a band of water that did not change between two bodies that did. The same
pass returns a coverage fraction, which is the alpha ramp that turned the coast from a dropped
quad into a fade. What is deliberately **not** smoothed is the interior: the 26 degC crossing
jumps between Levels and that quantisation is in the data, which `hazard.py` documents as the
limitation to state rather than hide.

**A blob a viewer cannot isolate is a blob they cannot read.** Every sentence on the Anomaly
Feature panel is measured over one box of water, and until "Show only this body of water" existed
that box could not be seen: a coloured patch inside a solid block says *that* water departed and
nothing about where it starts, how deep it runs, or whether it is one body or three. Two things
the clip alone did not solve, both measured: the remaining body needs about four times the
opacity, because the ray no longer accumulates anything on its way through; and the view has to
**pan** onto it, not zoom - `focusOn`'s fixed radius is right for a Float and collapses the block
frame to a diagonal for a body five degrees across.

**The Volume texture's v axis is referenced to the SOUTH edge.** `toTexture` computes
`(uBoxMax.z - p.z) / span.z` and world z is *minus* latitude, so that expands to
`(lat - south) / (north - south)`: v = 0 is the southern edge, not the northern one. Anything
building a box in texture coordinates - `applyFocus` is the only one so far - must match. Written
north-referenced it mirrors the box about the region's centre line and gives no error at all:
the isolation clip showed -5.0N to 4.0N for a feature at 12.5N to 20.5N, about 1800 km from the
ring pointing at it. Measure a clip by projecting the feature's own corners and diffing the
rendered frame against a volume-off frame; `web/probe-isolate.mjs` does exactly that.

**A chart's depth axis is trimmed to the instrument, so everything drawn must be trimmed too.**
The Profile chart stops at the depth the Float or buoy actually reached, which is right - a buoy
whose deepest sensor is 180 m should not be squashed into the top of a 2000 m axis. The model has
values far below that, and drawing them puts the model curve outside the frame. Below the last
measurement there is nothing to compare against anyway, and comparing is the only thing the chart
is for. Extending the axis instead was tried and rejected: it drops the measured part of the
worst case from 69% of the plot to 30%.

**A marker points at the thing, not at its extreme.** An Anomaly Feature's marker and every
fact its panel reports come from the cell nearest the body's centre, never the peak cell. Placed
at the peak the ring sat a median 222 km from its own feature and 1063 km at worst, describing
water at the other end of it. `peak_value` is still reported, and labelled "at its strongest".

**Anything whose meaning changes with the Field must be built per Field, not written once.**
`describePalette()` and `describeIsosurface()` in `src/guide.ts` exist for this. A surface of
constant value is an isotherm, an isohaline or an isopycnal depending on what it cuts, and one
static entry written for temperature explained cyclone fuel to someone looking at density. The
same trap caught the Collocation verdict, which told users the model read "cooler than" the
float for a density field.

**A Field with no render hint gets the default, not the last Field's.** `selectField()` in
`store.ts` applies `emphasis` and `opacity` from the `FieldSpec` where one is given and from
`DEFAULT_EMPHASIS` / `DEFAULT_OPACITY` where it is not. It used to change nothing when a Field
declared nothing, so the hints leaked forwards: visiting Observation Coverage once left
Temperature with the gradient weighting switched off, which turns the thermocline into an
invisible band under an opaque warm lid while the guide panel still tells the reader to look
for it.

**A log scale needs a real zero and a gradient to bend, and neither was being checked.**
`supportsLog` asked only whether the range went below zero, so the toggle appeared on 11 of the
14 Fields and meant something on 3 - there are 19 Fields now, and the rule is what decides,
not the count. Two separate failures came out of that. On **Observation
Coverage** the palette is four flat bands whose edges sit at whole cast counts, and bending the
position along a palette moves every edge while the key beside it cannot move: measured, every
cell with **1, 2 or 3 casts painted as "4 or more casts"**, under a legend still saying
otherwise. On **Temperature** the curve is applied to the *window fraction*, so "log" gave half
the palette to the coldest water in a range starting at 2.60 degC - a logarithm of nothing. The
rule now is all three of: range starts at zero (within 5% of its span), the palette is not
banded, and the range never goes negative. That leaves heat potential, current speed and INCOIS's
error estimate. Anything encoding the same quantity twice must go through the curve too - the
current **arrows' length** did not, so under Log one arrow was short and dark at once.

**An isosurface through a diverging Field is two surfaces, not one.** `sampled.r - uIsoValue` is
a single signed crossing, so a contour of departure at +0.3 degC enclosed the water that warmed
and drew **nothing at all** for water that had cooled by two degrees - measured at 5.6% of the
frame simply absent, with nothing on screen admitting it. The mirror value is `1 - uIsoValue` in
the encoded range, each skin takes its colour from its own end of the palette, and the panel says
`±`. That also settles a second confusion: a reader seeing cream and dark brown was seeing **one**
value under a hard light, and the ambient floor is now 0.62 rather than 0.35.

**A derived surface may not enclose water this platform refuses to call a departure.** The
anomaly isosurface defaulted to 0.27 degC while `find_anomaly_features()` demands 0.5 degC *and*
two standard deviations before it will mark a body at all - so the default surface drew the
thermocline's ordinary seasonal breathing as a block full of blobs. The contour's floor is the
detector's own threshold, read from the manifest, so the surface and the rings agree.

**`openGroups[id] ?? true` means "absent is open", which is the opposite of what a collapsed
panel is for.** The map started complete, so the fallback never fired and nobody noticed. The
moment the panel was made an accordion, replacing the whole map with a single key, every
untouched group's entry became `undefined` and sprang open behind the one just opened. A group
is open when its entry is `=== true`. The accordion itself is gone - the user wanted groups
open together - so `toggleGroup` and `selectField` both **merge** into the previous map rather
than replacing it, and the map is kept complete. What actually fixed the fold was the tab strip,
not the accordion, and that stays.

**The chrome is a frame, and the fold figures move with it.** Three bands - the top bar, a bay
down each side, and the time axis along the foot - anchored to the edge of the glass, square
outside, opaque, meeting on shared rules. Nothing floats, so nothing carries a blur or a drop
shadow to explain why it floats. Each band measures its own height and publishes it
(`--topbar-height`, `--timeline-height`), and the bays are `calc(100%)` minus the two, so no band
has to guess at another's size. **There is no credits band.** A folded "Sources" line sat under
the time axis until the owner removed it on 2026-09-11, knowing the attribution for Argo, INCOIS,
Copernicus and NOAA is a licence obligation; every full attribution string is on
`provenance.html`, which the landing page links to and the console does not.

At 1366x768 the left bay has **663 px**, measured as the panel's own `clientHeight` at its cap
rather than read off `max-height`, which is a `calc()` and comes back unresolved - identical in
both themes. It was 635 with the credits band and 615 before that band was folded; the 636 this
file carried for a round was arithmetic rather than a measurement.

**The table below was re-measured on 2026-09-23** against the shipped build, as the panel's own
`scrollHeight`, in both themes, which still agree to the pixel. The bay did not move and the
377 px floor did not move. **Everything else did**, by 99 to 204 px, because a Field button
gained a unit and a render-kind line under its name and the Field count went from 14 to 19 - a
change `web/CLAUDE.md` records without re-measuring the table beside it. The 2026-09-07 column
is kept because the difference is the point:

| Panel state | 2026-09-07 | 2026-09-23 | Against the 663 px bay |
| --- | --- | --- | --- |
| all groups closed | 377 px | **377 px** | fits, unmoved |
| Variable alone | 477 px | **576 px** | fits |
| Colourbar alone | 572 px | **621 px** | fits, 42 px to spare |
| Variable + Colourbar | 672 px | **819 px** | over by 156, was 9 |
| bias | 918 px | **974 px** | over by 311 |
| everything open | 2,007 px | **2,211 px** | over by 1,548 |

**The colourbar switcher cost the Colourbar group 139 px and 108 of them are back.** Five labelled
swatches in a vertical list were 132 px; folded behind a row that carries the chip and the name of
the colourbar actually on screen, they are 24. That row is not a bare "more" affordance - shut, it
still reports, which is the same rule that lets a collapsed group carry its readout. The
**two-column grid lost on measurement and by more than the arithmetic said**: five rows become
three, so it should have halved 132 px, and measured it returns **12**. In a 144 px cell instead
of a 291 px one the widest label needs 173 px of text and gets about 83, so **all five wrap to two
lines** - three double-height rows are barely shorter than five single ones. The comment in
`styles.css` was right for a different reason than it gave: not four smudges, four wrapped
labels.

**The Colourbar group was the one group too tall to open on its own** - 333 px against 258 px of
room once the 377 px floor was paid in a 635 px bay. It opens alone with 42 px to spare now,
which is the one conclusion in this block that survived the re-measurement.

**What is left is older than the switcher and structural.** The floor is 377 px of group headers
before a single control is drawn, which leaves 286 px for whatever is open in the 663 px bay.
Opened one at a time **beside Variable** and measured rather than added up, on 2026-09-23,
against that 663 px bay - **5 of the 10 fit and 5 do not**, where in 2026-09-07's measurement it
was 7 and 3:

| Group, open beside Variable | Over the bay by |
| --- | --- |
| Colourbar | **+156** (was +9) |
| Drift | **+143** (was +45) |
| Model vs instruments, the bias map | **+510** (was +355) |
| Rendering | **+39** (fitted with 32 px to spare) |
| Instruments | **+23** (was not a problem) |
| Depth slice, Quality, Isosurface, Vertical section, Your own data | fit, by 2 to 50 px |

**Two of those five are new, and one of them is the row this file had already corrected once.**
The 2026-09-07 note said *"the arithmetic got Rendering wrong, calling it 62 px over where the
panel fits it with 32 to spare"* - and Rendering is 39 px over now. The bias group has never
fitted on its own; it is 597 px of measurements, and a readout may not be approximated for
layout. Closing Colourbar's 156 px is no longer a 30 px group header away, so nothing here is a
token tweak: it needs a control moved out of the group or the group split.

**Every one of those numbers moved three times during one session**, twice because a fix
elsewhere took height away: lifting the timeline off the credits cost the panel 50 px, and
turning the floating pill into a foot band cost it 31 more. A fold figure is a property of every
band at once, so re-measure it after touching any of them rather than after touching the panel.

**One signal fired uniformly stops being a signal.** Every label in the console used to be IBM
Plex Mono, uppercase, at 0.16-0.18em - group names, legend titles, guide headings, chart
captions, status pills and the anomaly panel's terms alike. Five marks of "technical" at once, on
everything, is not emphasis; it is the texture of the thing, and it was the single loudest reason
this console read as machine-generated. The split now is: **a name is language** and is set in
Chivo, sentence case; **a value is a value** and stays mono, tabular and untracked; the wordmark
is the one place letterspaced caps are still the point. Accent went the same way - it was on the
active tab, the active Field button, every readout, every caret and the mode switch at once, so
it had stopped marking interaction and become the colour scheme. A readout is ink now.

**And the second half of that, finished on 2026-09-22: the chrome has no accent at all.** The
first pass took the accent off readouts and left it on the tabs, the selected Field, the mode
switch and the dive button, which is where the owner found it - "the blue buttons don't make
sense simply because the landing page doesn't follow the theme". That is the right diagnosis
and it is not about the hue: **the landing page carries no chroma whatsoever**, black type on a
warm grey ground with a primary button that is an ink outline inverting to an ink fill, so any
accent in the console makes the two halves read as two products. `.dive`'s own comment claimed
it matched the landing page's fill while the landing page had no fill. `--primary` is ink now in
both themes, and **the accent survives only where it marks live data** - the colourbar, the two
chart curves, the section line, the drift line - because a measurement earns a colour and a
button does not. Measured by `probe-chrome.mjs`, all 22 roles clean in both themes and
`.dive` went up to 15.85:1 on light and 13.18:1 on dark.

**Yellow was asked for and refused, and the reason is the one-role rule.** `--secondary` is
already amber in eleven places and means a middling disagreement or a caution, and
`--swatch-track` is the float tracks. An accent in the same family would give one colour two
jobs, which is what got the `turbid` fronts palette thrown out for hiding those tracks. Also
worth knowing: **there is no yellow on the landing page to borrow.** The coloured letters a
reader sees in its eyebrow line are subpixel antialiasing, not paint - the only hue on that
page was the theme pill's knob, and that is ink now too.

**Taking the accent out exposed a hierarchy error it had been hiding.** The selected Field
button filled with `--primary`, which made it exactly as heavy as the dive button - and picking
a Field is a *state* while diving is the one action on the bar. While the fill was teal it read
as "the accented thing"; the moment it became ink it was the brightest block in the panel on
dark and the darkest on light. It is `--surface-highest`, a full-ink label at 600 and a 2 px
inset rule now: three cues instead of one, and the primary fill belongs to the dive button
alone. The `.field-meta` override that existed only to survive an accent ground went with it.

**A diverging pair must be named as a pair, or half of it moves when the accent does.**
`.stat-value.model-low` borrowed `--primary` and `.model-high` borrowed `--tertiary`, so "the
model reads low against high" was one accent and one problem colour rather than two ends of one
scale. Repointing the accent would have turned one end into plain ink and left the other coral.
They are `--readout-low` and `--readout-high` now, with the same two colours they always had
and the meaning attached to them.

**Hiding a control is not turning it off, and `selectField` is the only place that can.** The
same leak, one field along: `isoEnabled` was not reset, so switching from Temperature with the
isosurface on to Observation Coverage, INCOIS Cast Count or Current Speed left the shader
drawing slabs and vertical columns with **no control on screen to turn them off** - those Fields
declare `isosurface: false`, which correctly hides the checkbox and did nothing else. Anything a
`FieldSpec` can forbid must be reset by `selectField` when it forbids it, not merely hidden by
the panel. `pipeline/tests/test_field_specs.py` holds which Fields may offer one and why.
**And a third time, on 2026-09-24**: `hazardPreset()` set `showAnomalies: false`, and the
rings are drawn on the anomaly Field alone - so the line did nothing on heat potential, which
is the Field it was written for, and everything on the next Field the reader chose. A reader
who had been anywhere near cyclone mode reached Anomaly Features with the marks off and no
control on screen that had turned them off. `selectField` resets it now and `hazardPreset`
does not set it; `cases.ts`'s `calm()` dropped it too, where every step selects a Field
immediately afterwards and it could never have taken effect. `docs/BUGS.md` item 141.

**An instrument is not always an Argo float, and a number about them is not always the total.**
There are Floats and there are moorings, `reportingByKind()` splits them, and the count on
screen is the count *drawn at the Timestep on screen* - measured across the thirty-six steps, 190
to 219 Floats and 5 to 14 buoys, against a bake of 257 and 17. Anything that says "Argo floats"
and means "instruments" is wrong twice.

**Not every Field is a Volume, and drawing one as a Volume is drawing the wrong thing.**
ADR 0014. `FieldSpec.render` says which of four kinds a Field is. Three of the hazard Fields *are
a depth*, so they are drawn as a sheet sitting at that depth inside the block; two are a total for
the whole column, so they are draped on the sea surface; currents are arrows. The Volume mesh is
**hidden** for all of them - it still holds the last Field's texture, and leaving it visible puts
one Field's data on screen under another Field's name, which is the worst failure available here.

**A Field that is not a Volume ships as float32 on the Grid, and that is the first rule, not an
optimisation.** A reader reads *metres* off a depth sheet and kJ/cm2 off a drape. Byte-quantising
and depth-warping them would look identical on screen and would be answering a scientific
question from a rendering artefact, in the one place nobody would ever check. 8 KB a file.

**And that Field leaves the building as a `Surface`, never as a `Grid` with one Level.** The
API did not know the class existed: `servable_fields()` refused by a list of names, so
`GetCapabilities` advertised eighteen layers and the seven that are one number per location fell
through to `{"detail": "no grid for d26 at timestep 35"}` - JSON, with a 404, out of an endpoint
whose own capabilities document promises `<Exception>XML`. It was five of fourteen when
`docs/BUGS.md` item 104 was written and seven of eighteen when it was fixed, because
`oxygen_floor` and `fronts` joined the class at the September bake and a list of names cannot
notice that. `SURFACE_RENDER_KINDS` reads `FieldSpec.render` instead, and
`test_surfaces_over_standards.py` goes red on a render kind nothing handles. **Serving them
needed no recompute**: `web/public/data/surfaces/` already holds 252 files of 2016 float32
values, and 2016 is exactly the 56 x 36 analysis lattice, so `native_surface()` reads the file
the browser reads. The shape is the part worth getting right - CF's answer for a quantity with
no depth is no vertical coordinate at all, not a one-element one, and a depth axis on Depth of
26 degC, whose value *is* a depth, would be well-formed and false. Measured after: 18 layers
draw, 11 advertise an elevation dimension and the seven surfaces advertise none,
`GetFeatureInfo` reports `"depth": null`, and `elevation=5` against `elevation=500` is
byte-identical on `d26` and different on `temperature`.

**The scale has exactly one curve, in `web/src/transfer.ts`.** A TypeScript function and the
identical GLSL as a string, inlined by the ray marcher. The log scale was cut once because the
shader bent the water while the colourbar stayed straight - that was a bug, and a second copy is
what caused it. Anything that colours a value goes through `transfer()`; nothing reimplements it.
The same rule sends `colourOf` and `surfacePixels` in `palette.ts` through `liftedPalette`, so
the sheet, the drape and the swatch cannot disagree. ADR 0010, amended.

**Currents are numbers now, and every sentence that said otherwise had to move.** ADR 0013
supersedes 0011. They are a Field with a palette, an entry in the Variable selector, arrows on
the chosen depth and a real speed under the cursor read from the Grid. The old rule said a
tooltip with a speed in it meant something had gone wrong; the opposite is now true. The one
thing that must stay said out loud is the cost: **no account to view or use the platform, one
free Copernicus account to rebuild its data**, and the credential never leaves the bake machine.

**`flat` is a reserved word in GLSL, and the error points at the wrong line.** It is an
interpolation qualifier, so `vec3 flat = ...` fails to compile and the message names the line
*after* the declaration. Both new vertex shaders had it, both silently failed, and the geometry
was perfectly correct the whole time - so nothing looked wrong except that nothing was drawn.
`web/probe-hazard.mjs` caught it by diffing a frame against the same frame with the mesh hidden,
which is the method this project's history keeps proving is the only one that works.

**A mode is not a Field button.** "Set up a cyclone question" changes the Field, the Timestep,
the render hints and the anomaly rings in one press, and it lived inside the Variable group -
which meant it rendered under Ocean state, under Circulation and under Change, a cyclone shortcut
sitting beneath Salinity. It is a **mode** above the group now, Hazard is what the mode contains
rather than the fourth of five tabs, and `selectField` sets `hazardMode` from the Field's own
group so the two cannot disagree however the Field was chosen - a tab, a deep link, the tour or
the preset itself.

**A palette belongs to a Field. The *look* of it is the reader's.** There used to be a dropdown of
nine, seven of which named quantities the platform does not carry - picking `algae` drew
temperature in the colours of a chlorophyll measurement nobody had taken. That failure was **a
palette naming a quantity**, not a reader having a choice, and only the first half was worth
keeping. The Colourbar group offers three or four alternates now, and four things hold the line:
each is labelled by the colours it contains ("Navy to yellow", "Black to white") and never by an
ocean variable; a **diverging** Field is only offered diverging alternates, because its midpoint
is a real value the isosurface and the `±` readout both depend on; a **banded** palette is offered
nothing, because a gradient over Observation Coverage repaints 1, 2 and 3 casts as "4 or more";
and `store.activePalette()` is the **one** lookup all seven call sites go through, because a
second copy disagreeing with the first is what got the log scale cut. `selectField` resets it,
like `emphasis` and `isoEnabled`. `probe-palette.mjs` checks all four, and was made to fail on
purpose first. ADR 0010, amended.

**Never ship a derived Field that is plausible and wrong.** Geostrophic current speed was
prototyped and rejected: it reported 0.16 m/s for the Somali Current in peak monsoon against a
real 1.5-2.5 m/s, and put the fastest water in the block on the equator, where geostrophy does
not hold. Finite and physical-looking is not the bar. ADR 0010 carries the numbers.

**Both themes are real, and the scene is part of the theme.** Chrome responds to `data-theme`
in CSS, but the globe, coastlines, markers and box frame are drawn by us in WebGL and swap via
`OceanScene.setTheme()`. The palette lift is theme-aware too (identity on light, where cmocean
was designed to live), and the colourbar and the water read the same value so ADR 0007 still
holds. All three pages share one `localStorage` key.

**Anything drawn on screen needs to be named.** Floats and tracks were drawn for days with
nothing saying what they were. `src/ui/MapKey.tsx` is where that lives.

---

## Testing

TDD applies to the science: depth warp, volume encoding, grid interpolation, collocation, the
Argo parser, the glider index parser and cast reader, the adapter seam, and every derived Field - including the
five hazard ones, each of which is held to a hand-computable case because a wrong constant there
produces a number that is finite, smooth and completely believable. Not to glue, UI or shaders. It also
applies to anything we *serve* - the DAP2 and WMS endpoints are science leaving the building,
and `test_dap.py` checks them by opening them with a real `pydap` client rather than by
asserting on our own bytes. 511 tests currently, across 36 modules, and `pipeline/scripts/collect_tests.py`
writes what `provenance.html` says about them - so the public page cannot claim a suite that no
longer exists, which it did for a month: 11 modules, 123 tests, "67 passed", against 379 in 25.

When a test and the code disagree, work out which is wrong before changing either. Three times
the *test's* expectation was the wrong one: gravity-corrected depth, a fixture too small for the
minimum-points filter, and a coverage test that asserted the very artefact it should have caught
(`test_a_coarsely_sampled_cast_leaves_the_thin_surface_slabs_empty`, which called a bug
"honest, not a bug" in its own docstring).

Fixtures have been too small twice now. If a test clips a percentile, count how much of the
fixture the outliers are before believing the assertion.

## Style

Simple, boring code; the obvious solution over the clever one. No abstraction until something is
needed twice. Comments explain *why*, especially where the obvious approach was rejected for a
real reason. **No em dashes** anywhere - plain hyphens only.

**A download held twice is invisible until the window grows.** `ArgoErddapSource.fetch_profiles`
did `requests.get(...)` then handed `response.text` to the parser, so `requests` kept the body as
bytes while Python kept a decoded copy beside it. Measured against the live endpoint: **175.0 MB
of CSV at twelve Timesteps against 498.4 MB at thirty-six**, so the pair went from 350 MB to
1 GB before a single Profile object existed. The 36-step bake was killed for memory **twice, at
the identical point 19 minutes in** - sampling caught it stepping from 958 MB to over 3.6 GB
inside one 15-second window, immediately after "wrote 360 native grids". `parse_profiles` never
needed the string: `csv.reader` reads line by line either way, so it now takes a string **or an
iterable of lines** and the fetch streams `iter_lines` straight into it. Nothing else changed and
the third run finished in 36 minutes. **A buffer that is fine at one window size is not a
measurement that it is fine.**

## Known upstream quirks

- **INCOIS ERDDAP sends an incomplete certificate chain.** Browsers and curl hide it, Python
  does not. `pipeline/oceanverity/tls.py` supplies the missing intermediate.
- **`tds.hycom.org` and `coastwatch.pfeg.noaa.gov` are unreachable from this network.** Do not
  retry; see `docs/plan/00-data-sources-verified.md`.
- **Real Argo floats fail, and quality control is two layers.** Argo's own `_qc` flags are
  fetched beside every value and 3/4/9 are refused per channel; on top of that a regional
  salinity floor catches what the global standard passes, because one float here reported
  ~20 PSU - ADR 0008. Reading the flags more than doubled the usable observations, because
  asking for them meant also asking for the raw columns the fallback chain had always declared
  and never fetched: 93 floats became 221.
- **INCOIS's own Argo archive ends 2025-04-23**, fifteen months before their analysis. That is
  why the demo reads Ifremer - ADR 0009.
