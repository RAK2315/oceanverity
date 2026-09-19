# Product

Written by `/impeccable init` on 2026-09-05, from a crawl of this repo and one round of
questions. Every other Impeccable command reads this file and `DESIGN.md` before doing any work.

## Register

product

The console is the deliverable and the larger surface: eleven panel components under
`web/src/ui/` against one landing page. `web/index.html`, `provenance.html` and
`requirements.html` are **brand** surfaces and should be reviewed as such when they are the named
target - Impeccable picks register by first match on the task cue and the surface in focus, so
this field is the fallback rather than a ruling.

## Users

Four audiences, and the problem statement names three of them by hand.

- **An INCOIS forecaster or ocean scientist**, at a desk, mid-task. They already have the model
  output and they already have the float profiles; what they cannot do is look at the two
  together, at depth, and get a number for how far apart they are. They arrive knowing the
  vocabulary and wanting density, not onboarding.
- **A Smart India Hackathon judge**, at a table, for a few minutes, on whatever laptop is in
  front of them - often 1366x768. They will open the landing page, press one thing, and decide
  whether this is a visualisation or an instrument. The first screen has to answer that.
- **School and college students, and the general public**, at an outreach event or an exhibition
  screen. Fifteen variables in five groups is the right toolkit for a forecaster and the wrong
  first minute for anybody else, which is why `Explore` and kiosk mode exist as a second door.
- **A policymaker**, who needs the answer and the caveat in the same sentence.

The job in one line: **see what the model predicted and what the instruments measured, in the
same water, at every depth, with the disagreement quantified.**

## Product Purpose

A browser-native platform that renders INCOIS's own gridded ocean analysis as a GPU ray-marched
3D block you can fly into, overlays the Argo float and moored-buoy profiles measured in that
same water, and scores one against the other. Built for Smart India Hackathon 2026, PS 26067
(MoES / INCOIS), theme Disaster Management.

Success is a forecaster clicking one float and getting a comparison they trust, and a judge
being unable to find a number on screen that the platform cannot source. It opens in a browser,
needs no account, and makes **zero network calls at demo time** - a dead venue connection cannot
kill it.

## Brand Personality

**Precise, candid, unshowy.**

- **Precise** - every figure carries its unit, numbers are set in a monospace face so a changing
  digit does not shift the ones beside it, and a measurement always comes from the full-precision
  Grid rather than from the rendered picture.
- **Candid** - the platform publishes its own error. The drift model ships its median separation,
  the bias map prints floats and moored buoys separately because pooling them
  would flatter the model, and Observation Coverage exists to say where nobody looked instead of
  colouring it in. `docs/BUGS.md` is a public defect list.
- **Unshowy** - `styles.css` opens by calling this "an instrument, not a consumer app". Panels
  recede. Nothing is animated that is not reporting a state change. The one place ambition is
  allowed is the water itself, and the water is not chrome.

Voice: plain words, short sentences, no marketing verbs. Say what a control does and what it
costs. When a question is simplified for a wider audience, the caveat travels **beside** the
answer and never after it.

## Anti-references

All four were named explicitly. Each has a live foothold in the current build, which is why they
are worth writing down rather than assuming.

- **The SaaS landing template.** Gradient hero, three pricing cards, a logo wall, a "trusted by"
  strip, a big-number metric row. `.hero-stats` is one step from the metric-row version of this,
  and an `.eyebrow` currently sits above seven of seven sections.
- **The sci-fi HUD.** Glowing rings, fake telemetry, decorative glassmorphism. The real danger
  for an ocean console: the panels already lean on `backdrop-filter`, and every blur has to be
  earning its place rather than signalling "advanced".
- **The government portal.** Dense navy tables, seals and crests, every route ending in a PDF.
  The MoES / INCOIS association pulls this way and must be resisted; provenance is shown by
  linking the live figure to its source, not by looking official.
- **The consumer weather app.** Cartoon icons, pastel rounded cards, one big number and a mood.
  The exact opposite of putting a number on the disagreement.

## Design Principles

1. **Never answer a scientific question from the picture.** The Volume is quantised,
   depth-warped and back-filled across land for the GPU's benefit. Anything a user reads as a
   measurement comes from the Grid. This governs the interface too: a readout is a measurement,
   so it may not be approximated for layout.
2. **Say what you do not know.** A gap is drawn as a gap, a hollow marker never measured that
   variable, and a simplification carries its caveat beside it. Absence is information and gets
   the same design attention as presence.
3. **The left panel says what and how much; the guide panel says why.** A sentence on the left
   that explains rather than reports belongs on the right, and a figure on the right that is
   already a readout on the left belongs on the left. Neither should do both.
4. **Every control is explained and reachable.** If it exists it has a `guide.ts` entry, and the
   guided tour visits it. Two probes fail otherwise. An unexplained control is worse than no
   control.
5. **Measure it, do not look at it.** Every bad rendering bug in this project's history looked
   like a shader bug and was not. "Cosmetic" is a claim, so it gets measured before it is
   believed - including claims that a redesign improved something.

## Accessibility & Inclusion

**WCAG 2.2 AA, in both themes.**

- Body text at 4.5:1 and large text at 3:1 against the ground actually behind it, in light and
  in dark. `web/probe-landing.mjs` already measures the hero this way at 1600 px and 1280 px and
  fails if the two themes separate by more than 0.05.
- Both themes are real and the scene is part of the theme: chrome follows `data-theme`, and the
  globe, coastlines, markers and box frame swap through `OceanScene.setTheme()`. A change checked
  in only one theme is a change that has not been checked.
- Keyboard reachable throughout. Anything clickable is a real `<button>` - the timeline's tick
  strip was a mouse-only duplicate until it was fixed, and that is the failure mode to watch.
- `prefers-reduced-motion: reduce` is honoured on the landing page and in the console, and the
  reveal animation degrades to fully visible rather than gating content on a transition.
- Kiosk mode is a distinct accessibility context, not a CSS state: type at reading-across-a-room
  size, no console chrome, and a reset a minute after the last visitor leaves.
- **Out of scope by decision:** the cmocean data palettes. They are lifted per theme in
  `palette.ts` so the colourbar and the water agree, and ADR 0010 deleted the chooser on purpose.
  Colour-blind safety of the *chrome* roles is in scope; recolouring the data is not.
