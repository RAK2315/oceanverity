# Where every number comes from, and which ones to trust

Written 2026-09-13, after a deck review in which five figures in one afternoon turned out to be
wrong or unsupported. None of them was a bug in the platform. Every one was a number copied from
somewhere other than the data.

**The rule, in one line: a number is only as good as the file it was read from, so name the file.**

---

## The places numbers live, most trusted first

| # | Where | Trust | Why |
| --- | --- | --- | --- |
| 1 | `web/public/data/*.json` - the build's own data: `manifest.json`, `residuals.json`, `collocations.json`, `drift.json`, `tests.json`, `hazard_check.json`, `cases/montha.json` | **Source of truth** | Written by the pipeline from the real data. Everything else should be read from here. |
| 2 | `ppt/FACTS.md` | **Trusted** | Generated from #1 by `collect_facts.py`, with the source of every row. Re-run it; never edit it. |
| 3 | Pages that read #1 live: `provenance.html`, `requirements.html`, the app's guide panel (`{token}`s), the storm walkthrough | **Trusted** | They fetch the figure when the page opens, so they cannot go stale. |
| 4 | Figures typed into documents: `README.md`, `docs/README-full.md`, `docs/demo/`, `web/index.html`'s `data-measure` strings, `scripts/dossier.html`, `scripts/ppt_diagrams.html`, `ppt/DECK.md`, `ppt/NOTES.md` | **Check before quoting** | Correct on the day they were typed. `check_figures.py` finds the ones that have drifted. |
| 5 | Decision records, `docs/BUGS.md`, `docs/plan/`, `CLAUDE.md` | **History** | They quote figures *as they were* on purpose ("at twelve Timesteps it was nine buoys"). Never quote them as current. |
| 6 | Screenshots in `assets/screenshots/` and the three image folders | **Stale** | The data was generated on **9 Sep 2026**; every committed screenshot was last changed on **5 Sep or earlier**. `bias.jpg` shows 230 instruments, 9 buoys and 12 analyses. Check the counts and the timeline in a picture before using it. |
| 7 | Handoffs, research artifacts, chat | **Not a source** | Useful for leads. Two findings from them were wrong (below). Verify against #1 before use. |
| 8 | `ppt/script-v1-recorded.md` - the video already recorded | **Locked** | It cannot change, so it is allowed to disagree. The deck and the site must not copy from it. `ppt/script.md` (version 2, 2026-09-20) is the script for the next recording and is checked like the deck. |

---

## What went wrong on 2026-09-13, and what each one teaches

| Figure | Where it came from | What was actually true | Lesson |
| --- | --- | --- | --- |
| Buoys disagree **5.5x** more than floats | `residuals.json`, correctly read | The ratio mixes depths: floats are compared to a median **1,967 m**, buoys to **500 m**, and deep water is easy for the model. Over the same top 100 m the gap shrinks to well under 2x. One buoy also sent a broken reading. | A correct number can still be the wrong comparison. `FACTS.md` now prints the depths beside the two gaps. |
| Buoy typical gap **1.01 degC** | `residuals.json` | Buoys 23094 and 23456 reported **0.0 degC at 20 m** (a dead sensor or fill value) that passed the range check. The Argo spike test now refuses them: 24 readings, and the gap is **0.88 degC**. | The buoy feed has no quality flags. `osmc.reject_spikes` is the second check. |
| 0.61 and 0.82 degC "on the same depths" | A quick calculation in chat | Never in the build, and the dates were not matched. | An estimate made in chat is not a figure. Put it in the pipeline or do not quote it. |
| Buoy 23093 "directly in the track" of Cyclone Montha | Research artifact | IMD's best track puts it **534 km** away; 23459 is **271 km** away. | Measure distances to the official track, never to a news map or a guess. |
| Mixed layer "deepened from 11 m to 33 m" | One grid cell, from the research artifact | That cell is about 200 km off the track. Within 150 km of the track the median did not deepen. | A single cell is a cherry-pick. `storm.change_near_track` compares near against far. |
| Copernicus reanalysis "ends in 2022" | Research artifact | `docs/plan/04` measured **2026-06-23** on 1 Sep, and Copernicus's own catalogue (STAC) still shows 1993-01-01 to 2026-06-23 on 14 Sep. "2022" was out of date. | When two sources disagree, write the sentence that is true under both, and say which was measured. |

---

## How to check a number, every time

```bash
cd pipeline
../.venv/Scripts/python scripts/collect_facts.py     # what the figures are      -> ppt/FACTS.md
../.venv/Scripts/python scripts/check_figures.py     # where they are written wrong (exit 1 if a current document is)
```

1. Look the figure up in `ppt/FACTS.md`. If it is not there, it is not a build figure yet.
2. If you need a new figure, add it to the pipeline (a script that writes JSON) and to
   `collect_facts.py`. Do not calculate it by hand and paste it.
3. After any bake, refresh or new test, run both commands and fix every **CURRENT** line.
4. Before using a screenshot, read its counts and timeline off the picture and compare them
   with `FACTS.md`.

`check_figures.py` checks **twenty-two** figures people actually quote. Twelve are the originals:
tests, browser probes, moored buoys, analyses, instruments, the two typical gaps, the
floats-to-buoys ratio (always flagged), the coverage gap, drift floats, the window length and
variables. Ten were added on 2026-09-23, after the audit in
[`audit/2026-09-22-audit.md`](audit/2026-09-22-audit.md) found every one of them written down
wrong somewhere in a run that reported **no current mismatch at all**: the baked size in MB, the
adapter count, the provider count, the explained-control count, the tour steps, the Explore
questions, the REST and total route counts, the size of a float pool a gap was measured over,
and the drift cycle count.

Three holes were closed with them, and they are worth knowing because each is a way a figure
hides:

- **It used to read line by line.** Prose here wraps at about 96 characters, so "Fifteen /
  variables in five groups" put the number and its noun on different lines and nothing saw it -
  in `web/src`, which is a checked root, for a figure it already knew. It reads across the wrap
  now and reports only matches that cross the boundary.
- **It used to skip `api/`, the probes, `DESIGN.md` and this file.** Three `api/` docstrings
  framed the service around a Field count four rounds old, and the file that tells everyone else
  to check their figures was in neither list.
- **A year is not a count.** Widening the patterns made "the September 2026 Fields" a mismatch,
  so a bare four-digit year is skipped for any figure that could not legitimately be one.

It is still narrow on purpose, and a document it passes is still not proven right, only not
caught wrong.

---

## Figures still wrong in documents

**Run `check_figures.py`. It is the list.** This section used to name three files and was wrong
about two of them within a week, because a hand-kept list of stale figures goes stale exactly
the way the figures do. On 2026-09-23 the script reports **0 current** mismatches over
twenty-two figures and twenty-six roots, and everything it lists under HISTORY is quoted as it was on
purpose.

Moving targets to expect: the **test count** moves whenever a test is added, the **probe count**
whenever a probe is, and the **baked size** whenever the bake window does. All three are read
from the build; anything typing them by hand will drift again.
