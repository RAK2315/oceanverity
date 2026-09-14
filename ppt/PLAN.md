# Deck plan, 2026-09-13 - small changes, every figure checked

The Canva deck stays as it is. This lists only what has to change because something on it is no
longer true, and the few places the two new features give a slide a stronger sentence. **Every
figure here is in `ppt/FACTS.md`** (regenerate with `collect_facts.py`) or has its source beside it.
Where something is not verified, it says so.

Nothing in the app changed that the video shows, except numbers the video does not speak - see
the last section.

---

## What the research found (checked on 2026-09-13)

| Claim | Finding | Source |
| --- | --- | --- |
| "INCOIS stopped publishing cyclone heat potential in 2019" | **False.** INCOIS publish TCHP daily from their forecast models (frames dated 11-13 Sep 2026), and serve TCHP and mixed layer depth as map layers. What ended on 2019-03-30 is the series computed from their **Argo analysis** on ERDDAP. | [incois.gov.in/site/services/tchp.jsp](https://incois.gov.in/site/services/tchp.jsp), [incois.gov.in/oceanservices/rsmc_ocean.jsp](https://incois.gov.in/oceanservices/rsmc_ocean.jsp), `incois_valueadded_products_datasets` |
| Our hazard fields are right | **Checked, for the first time.** Run over 183 dates from 2004-2019 against INCOIS's own published values: depth of 26 degC is the same number in 97.2% of cells, depth of 20 degC in 98.7%. INCOIS's mixed layer uses 0.5 degC below the 10 m value; with that rule ours match in 92.0%. Ours use the stricter de Boyer Montegut rule, so read shallower - a definition, not an error. | `hazard_check.json`, `FACTS.md` |
| Buoys disagree "5.5x" more than floats | **Not like for like.** Floats are compared to a median 1,967 m, buoys to 500 m. Two buoys also sent 0.0 degC readings at 20 m, now refused: buoys 0.88 degC, floats 0.18 degC. | `residuals.json`, `FACTS.md` |
| Cyclone Montha facts | **Verified from IMD's best track.** Depression 25 Oct 2025, severe cyclonic storm 28 Oct, peak 50 kt, crossed the coast near Narsapur on 28 Oct, weakened 30 Oct. | IMD RSMC New Delhi best track, `data/storms/` |
| A buoy was "under the storm" | **False.** Nearest moored buoy 23459 is 274 km from the track; 23093 is 534 km. An Argo float did surface 3 km from it. | `cases/montha.json` |
| Mixed layer "deepened 11 m to 33 m" | **A single cell 200 km off the track.** Within 150 km of the track the median did not deepen. Use heat potential and surface cooling instead (below). | `cases/montha.json` |
| INCOIS LAS is 2D | **Fair.** LAS offers maps, time series, Hovmoller and area averages - 2D plots, no 3D volume. Do not say "one depth at a time": whether INCOIS's LAS plots depth sections was not verified either way. | INCOIS LAS paper (ResearchGate, "INCOIS Live Access Server"), `las.incois.gov.in` |
| Deadline | **20 September 2026** on the PS page as mirrored by community sites. Not checked on sih.gov.in itself - check the portal. | SIH 2026 explorer mirror |

---

## Slide by slide

### Slide 1 - no change

### Slide 2 - Proposed solution

- **The chart.** Remove the 0.6/0.8 bars and the `5×` block (not in the build, and not like for like).
  Two honest options, pick one:
  - **Words, no chart:** `Checked against water the model never saw: 266 instruments, with the 17 moored buoys it did not ingest reported on their own.`
  - **A fresh screenshot** of the storm walkthrough, step 3 (heat potential after the storm, IMD track on the water). It is new, it is a real event, and it answers "show me it doing its job". Needs a fresh grab - every committed screenshot predates the current data.
- **Innovation, "Cyclone fuel maps, rebuilt":** body becomes
  `Depth of 26 °C, heat potential, mixed layer depth and two more, from INCOIS's Argo analysis - and checked against INCOIS's own published archive: the same number in 97% of cells.`
  Why: it replaces a claim that is false ("INCOIS stopped") with one that is measured.

### Slide 3 - Technical approach

- Diagram box `Cyclone hazard fields - stopped in 2019, rebuilt here` → `Cyclone hazard fields - checked against INCOIS's archive`.
- Tech stack: no change.

### Slide 4 - Feasibility

- Top strip: `409 automated tests and 15 browser checks` → read the current counts from `FACTS.md` (430 and 16 today; they move whenever a test is added).
- Add, or swap for the weakest row, one risk-and-answer pair:
  - Risk: `Our recomputed cyclone fields could be wrong.`
  - Answer: `We ran our code over 15 years INCOIS published themselves: the same numbers in 97% of cells for the 26 °C depth.`

### Slide 5 - Impact

- **Impact 3 blue line:** `Warm water at depth helps a storm strengthen. Five fields, computed in 3D beside the instruments and checked against INCOIS's own archive.`
- **Montha box** - replace the mixed-layer chart and the 0.91/0.20 pair with what was measured along IMD's own track (all in `FACTS.md`, section "Cyclone Montha"):
  - Headline: `CYCLONE MONTHA, BAY OF BENGAL, OCT 2025`
  - Pair: `76 → 65 kJ/cm²` labelled `heat available to a storm, within 150 km of its track, 20 → 30 Oct` and `62 → 74` labelled `the same bay, far from the track`
  - Line: `Near the track the median fell; far from it, it rose.` (Near: 93% of cells fell. Far: only 53% rose, so do not say "gained everywhere".)
  - Caveat (keep): `Ten-day analyses, so this is the days it crossed, not the storm alone. Track: IMD best track.`
  - Optional second line: `Nearest moored buoy, 274 km away, measured −0.58 °C at 10 m; the analysis showed −0.25 °C.`
- The d26 image: keep only if it is re-grabbed; the caption must drop "INCOIS stopped publishing this in 2019".

### Slide 6 - Research and references

- Evidence caption 2: `Cyclone heat potential - computed here from INCOIS's Argo analysis` (drop "public series ends 2019").
- Links: add `A real storm, step by step - rak2315.github.io/samudra-sih26/app.html?case=montha` **only after the build is deployed**. It does not exist on the live site yet.
- References: add `India Meteorological Department (2026). RSMC New Delhi best track data, 1982-2026.`
- `<your video link>` still to fill.

---

## The video (locked) against the site after today

| The video says | The site will say after deploy | Risk |
| --- | --- | --- |
| "just over a degree" for the buoys | 0.88 °C | Small. Say in Q&A: a broken buoy reading was found and removed after recording. |
| "five and a half times" | no ratio quoted | Same answer. |
| "nine point nine percent" | 10.2% | Known, unchanged. |

## Screenshots

Every committed screenshot was taken before the current data (9 Sep). Before any goes on a slide,
read its counts and timeline off the picture against `FACTS.md`, or grab a fresh one.
