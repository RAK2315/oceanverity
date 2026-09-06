---
name: Samudra 3D
description: A forecaster's console for the Indian Ocean - dark by default, monospaced where it counts, and honest about what it does not know.
colors:
  surface: "#0f1415"
  surface-lowest: "#0a0f10"
  surface-low: "#171d1d"
  surface-mid: "#1b2121"
  surface-high: "#252b2c"
  surface-highest: "#303636"
  on-surface: "#dee3e4"
  on-surface-variant: "#bcc9ca"
  on-surface-faint: "#869394"
  outline: "#4b5859"
  outline-variant: "#2c3536"
  primary: "#64d7e3"
  primary-strong: "#3fb8c4"
  primary-hover: "#86e5ef"
  on-primary: "#00363b"
  secondary: "#fabc45"
  tertiary: "#ff9e8b"
  good: "#5fd68a"
  observed: "#64d7e3"
  model: "#bcc9ca"
  chlorophyll: "#7ddc9f"
  surface-light: "#f4f9f9"
  surface-lowest-light: "#ffffff"
  surface-low-light: "#eef4f4"
  surface-mid-light: "#e7eeee"
  surface-high-light: "#dfe7e7"
  surface-highest-light: "#d5dede"
  on-surface-light: "#131a1b"
  on-surface-variant-light: "#3b4849"
  on-surface-faint-light: "#5f6d6e"
  outline-light: "#97a4a5"
  outline-variant-light: "#c8d2d2"
  primary-light: "#00666e"
  primary-strong-light: "#00838d"
  primary-hover-light: "#00858f"
  on-primary-light: "#ffffff"
  secondary-light: "#8a5c00"
  tertiary-light: "#b23a22"
  good-light: "#1d7a45"
  observed-light: "#00666e"
  model-light: "#5f6d6e"
  chlorophyll-light: "#17703f"
  frame: "#0d1213"
  frame-rule: "#313b3c"
  frame-inset: "#12191a"
  frame-light: "#f7fbfb"
  frame-rule-light: "#c2cdcd"
  frame-inset-light: "#eef4f4"
  viewport-crest: "#12243a"
  viewport-mid: "#0a1526"
  viewport-abyss: "#03060b"
  viewport-crest-light: "#f0f9fc"
  viewport-mid-light: "#dcecf3"
  viewport-abyss-light: "#cbe1eb"
  scene-drift: "#c39bff"
  scene-drift-light: "#6b3fc4"
  scene-section: "#63e6c4"
  scene-section-light: "#0b7a63"
  feature-warm: "#d8663f"
  feature-cool: "#4a8fd0"
  speed-ramp-0: "#fffcf4"
  speed-ramp-1: "#a4d5a0"
  speed-ramp-2: "#3f9b8e"
  speed-ramp-3: "#24555f"
typography:
  display:
    fontFamily: "Chivo, 'Helvetica Neue', Arial, system-ui, sans-serif"
    fontSize: "clamp(40px, 6.6vw, 92px)"
    fontWeight: 800
    lineHeight: 0.98
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Chivo, 'Helvetica Neue', Arial, system-ui, sans-serif"
    fontSize: "clamp(28px, 3.4vw, 44px)"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Chivo, 'Helvetica Neue', Arial, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Chivo, 'Helvetica Neue', Arial, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  label:
    fontFamily: "Chivo, 'Helvetica Neue', Arial, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.005em"
  readout:
    fontFamily: "'IBM Plex Mono', ui-monospace, 'Cascadia Mono', Consolas, monospace"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0.04em"
rounded:
  hairline: "1px"
  hairline-thick: "2px"
  chip: "3px"
  xs: "4px"
  thumb: "5px"
  control: "6px"
  sm: "8px"
  md: "12px"
  card: "14px"
  card-lg: "16px"
  sheet: "18px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "13px"
  lg: "16px"
  gutter: "18px"
  section: "26px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: "11px 20px"
    typography: "{typography.body}"
    height: "34px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.on-primary}"
  button-ghost:
    backgroundColor: "{colors.surface-low}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.sm}"
    padding: "0 14px"
    height: "34px"
  button-icon:
    backgroundColor: "{colors.surface-low}"
    textColor: "{colors.on-surface-variant}"
    rounded: "{rounded.pill}"
    width: "34px"
    height: "34px"
  panel:
    backgroundColor: "{colors.frame}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.hairline}"
    width: "344px"
  control-group-head:
    textColor: "{colors.on-surface}"
    typography: "{typography.label}"
    padding: "7px 16px"
  control-group-head-hover:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-surface}"
  segmented-item:
    backgroundColor: "{colors.surface-low}"
    textColor: "{colors.on-surface-variant}"
    rounded: "{rounded.xs}"
    typography: "{typography.readout}"
  segmented-item-selected:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
  readout:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.readout}"
---

# Samudra 3D

## Overview

**The Creative North Star: the bridge instrument.**

A console bolted to a ship's bridge, not an app. It is dark because it is read at night over a
lit chart; every dial is labelled because the person reading it is not the person who built it;
and nothing on it moves unless the thing it measures moved. Its authority comes from being
specific, not from looking advanced.

`web/src/styles.css` opens by saying it in one line - *"an instrument, not a consumer app"* -
and everything below follows from that. Panels recede so the water is the subject. Numbers are
monospaced so a column of readings lines up and a changing digit does not shift its neighbours.

**The chrome is a frame, not a deck of cards.** Every surface used to be a rounded panel hovering
over the water with a hairline, a blur and a drop shadow - one idea applied ten times, which is
what made it read as generated. It is four bands now: the top bar, a bay down each side, and a
foot holding the time axis over the credits. They are anchored to the edge of the glass, square
on the outside, opaque, and meet on shared rules. Each band measures its own height and publishes
it, so the bays are exactly as tall as the gap between the other two.

The mood is **precise, candid, unshowy**, carried straight from `PRODUCT.md`. Candid is the one
that shows up visually: a gap is drawn as a gap, a hollow marker means "never measured this", and
a caveat sits beside its answer rather than under it in small print.

**What it must not feel like**, all four named explicitly: a SaaS landing template, a sci-fi HUD,
a government portal, or a consumer weather app. The nearest live risk is the third of those on
the landing page and the second in the console, where `backdrop-filter` is load-bearing on four
surfaces and could easily read as decoration.

**Two themes are both real, and the scene is part of the theme.** Chrome responds to
`data-theme` on `<html>`; the globe, coastlines, markers and box frame are drawn in WebGL and
swap through `OceanScene.setTheme()`. All three pages share one `localStorage` key. A change
checked in one theme has not been checked.

**One exception, and it is deliberate:** the viewport behind the canvas keeps a deep ocean ground
in both themes, and `.hero` on the landing page re-declares the dark palette for everything
inside it. The cmocean palettes are lifted for a dark backdrop, so pale water on a pale page
loses the contrast that makes the thermocline legible. Both are scientific decisions wearing
visual clothes.

**Layout.** The console is a framed viewport: a 344 px bay left, a 348 px bay right, a bar
across the top and a foot across the bottom, with the water in the rectangle between them. The
bands measure each other rather than sharing a grid - the bays take their height from
`--topbar-height`, `--timeline-height` and `--attribution-height`, each published by the component
that owns it, and the map key and the depth caption read their neighbours'
`getBoundingClientRect()` and step clear, because a fixed offset is wrong at the next viewport.
The landing page is the opposite: a 1400 px shell, and a hero that is two columns - the headline
and its actions left, a live WebGL globe right - over a five-cell stat strip. The globe is hidden
below 1180 px and the hero becomes one column.

**Density is a feature.** The reference viewport is 1366x768, where the left bay has **615 px**
between the bar and the foot. Anything added to it costs something already on screen. Measured
there: all groups closed **347 px**, Variable alone 446, Variable and Colourbar together **615 -
which is exactly the height available**, and every group open 2,403.

## Colors

Strategy: **restrained**. Tinted neutrals carry the surface; one accent carries interaction.
Everything else is a named role that appears only when its condition is true.

Six surface levels rather than shadows do most of the work. Every panel picks a level rather than
inventing a colour.

| Role | Dark | Light | What it means |
| --- | --- | --- | --- |
| `--surface` … `--surface-highest` | `#0f1415` → `#303636` | `#f4f9f9` → `#d5dede` | Tonal layering. Six steps, darkest first on dark and lightest first on light. |
| `--on-surface` | `#dee3e4` | `#131a1b` | Body ink. |
| `--on-surface-variant` | `#bcc9ca` | `#3b4849` | Secondary ink: labels, slider heads, bullet text. |
| `--on-surface-faint` | `#869394` | `#5f6d6e` | Tertiary ink: notes, units, disabled. The one to watch for contrast. |
| `--outline` / `--outline-variant` | `#4b5859` / `#2c3536` | `#97a4a5` / `#c8d2d2` | Hairlines. Variant is a divider, plain is a border you should see. |
| `--primary` | `#64d7e3` cyan | `#00666e` deep teal | **Interaction, and only interaction.** Selected, focused, pressable, live. |
| `--secondary` | `#fabc45` amber | `#8a5c00` | The one number that matters, and a caveat. Never decoration. |
| `--tertiary` | `#ff9e8b` coral | `#b23a22` | A problem, only. |
| `--good` | `#5fd68a` | `#1d7a45` | Something resolved, only. |
| `--observed` / `--model` | cyan / grey | teal / grey | Chart-only roles so the two curves keep their identity across themes. The model curve is also dashed, so the pair does not rely on hue. |
| `--chlorophyll` | `#7ddc9f` | `#17703f` | Its own role rather than borrowing `--good`, which means "resolved" everywhere else. |

The accent inverts in lightness between themes (`#64d7e3` → `#00666e`) rather than being reused,
because a pale cyan on white is unreadable and a deep teal on near-black is invisible. Anything
new must do the same.

**Out of scope: the data palettes.** cmocean scales belong to a Field, are lifted per theme in
`web/src/palette.ts` so the water and the colourbar agree, and there is deliberately no chooser
(ADR 0010). Recolouring the chrome is design work; recolouring the data is not.

**Three literal-colour sets are deliberate and are not drift.** A detector reads them as
undocumented colours, so they are named here rather than left to be "fixed" by someone tidying:

- **The viewport ground** (`viewport-*`). A radial gradient behind the canvas, deep in both
  themes for the reason in Overview. It is a backdrop, not a surface, and does not belong on the
  surface ramp.
- **The scene-bridge swatches** (`scene-drift`, `scene-section`). These are CSS copies of
  `SCENE_COLOURS` in `OceanScene.ts`. There is no way to share a `THREE.Color` with a
  stylesheet, so the map key names them next to the scene that draws them. **If one moves, both
  move**, and the map key is the only place the pairing is visible.
- **The feature chips** (`feature-warm`, `feature-cool`) and the currents swatch, which is the
  literal cmocean speed ramp `#fffcf4 → #a4d5a0 → #3f9b8e → #24555f`. Both take their colour from
  the data they describe, so a chip and the ring in the water agree. Same rule as ADR 0007.

**Hairline radii are geometry, not shape.** `1px`, `2px` and `3px` appear on 3px slider tracks,
16x3px line swatches and a 12px colourbar. They round a hairline; they are not container shapes
and they do not belong to the card scale.

**Contrast target: WCAG 2.2 AA in both themes.** `probe-landing.mjs` measures the hero against
the rendered ground beneath it at 1600 px and 1280 px and fails if the two themes separate by
more than 0.05. Measured after the redesign: headline **10.19** and 11.02, accent **6.80** and
7.23, the hero's own figures 14.47 and 14.75. Every text role in the console chrome was measured
in both themes as well, and none of the twenty fails.

## Typography

Self-hosted from `web/public/fonts/`, on a hard rule: **no external request, ever**. A Google
Fonts link is a build failure, not a style choice.

**The console and the landing page do not currently share a typeface, and that is unresolved.**
The console sets Chivo and IBM Plex Mono; `index.html`, since the globe hero arrived, sets Space
Grotesk and Inter. All four are self-hosted so the rule above still holds, but two halves of one
product reading as two products is a real cost. It needs a decision between the teams, not a
unilateral fix, so it is written down here rather than quietly reconciled.

In the console:

- **Chivo** (400 / 500 / 700 / 900) for everything read as language.
- **IBM Plex Mono** (400 / 500) for everything read as a value: readouts, labels, dates,
  coordinates, statistics, axis figures.

On the landing page: **Space Grotesk** for display and every uppercase caption, **Inter** for
body.

The split is not decorative. A monospace face is what keeps a column of readings aligned and
stops a changing digit from shifting the ones beside it during playback.

| Role | Size | Weight | Tracking | Where |
| --- | --- | --- | --- | --- |
| display | `clamp(40px, 6.6vw, 92px)` | 800 | -0.035em | Landing hero only |
| headline | `clamp(28px, 3.4vw, 44px)` | 800 | -0.025em | Landing section headings |
| title | 17px | 700 | -0.01em | Panel titles |
| body | 13px | 400 | normal | Console body |
| label | 13px Chivo | 600 | -0.005em, sentence case | Every group heading |
| readout | 12px mono | 400 | 0 | Every live figure |

**Three roles, not one signal repeated.** Every label in the console used to be IBM Plex Mono,
uppercase, at 0.16-0.18em - five signals of "technical" fired at once and applied uniformly to
group names, legend titles, guide headings, chart captions, status pills and panel terms alike.
Fired uniformly a signal stops being a signal and becomes the texture of the thing, and it was
the single loudest reason this console read as generated. So: **names are language** and are set
in Chivo, sentence case; **values are values** and stay mono, tabular, untracked; **micro-labels**
keep mono where a unit needs it but lose the uppercase tracking. The wordmark is the one place
letterspaced caps are still the point.

The scale is fixed in the console (product register: users are at consistent DPI, and a fluid
heading inside a 344 px panel looks worse, not better) and fluid on the landing page.

**Known discrepancy:** `display` and `headline` ask for weight 800 and no 800 face ships, so the
browser resolves upward to 900. It is not broken, but the weight on screen is not the weight in
the file. Either ship 800 or write 900.

Prose is capped at 65-75ch. The guide panel is held tighter still by `probe-guide.mjs`: one
sentence of definition plus bullets, **max 4 bullets, max 2 lines each**, median 113 words
measured across all 43 entries.

## Elevation

**Tonal first, shadow second.** Depth is carried by the six surface levels; shadows only separate
a floating surface from the canvas behind it, which is the one place tone cannot do the job.

| Token | Dark | Light |
| --- | --- | --- |
| `--shadow-panel` | `0 18px 46px rgba(0,0,0,0.5)` | `0 18px 40px rgba(19,26,27,0.16)` |
| `--shadow-raised` | `0 8px 22px rgba(0,0,0,0.38)` | `0 8px 20px rgba(19,26,27,0.12)` |

Shadows lighten substantially on the light theme, because a heavy drop shadow on white reads as
a mistake.

**There is no blur left in the chrome, and no shadow on a bay.** Four surfaces used to carry a
14 px `backdrop-filter` on the argument that they float over moving water and the text would
vibrate without it. The bands are opaque now, which answers the same problem better and more
honestly - the old panel ground was 97% opaque *and* blurred, which is the cost of glass with
none of the effect, because at that alpha there is nothing to see through. Shadows survive only
on the two things that genuinely do float: the map key, which is draggable, and the cue. A new
blur needs an argument opacity cannot answer, or it does not exist.

A semantic stacking order is in use rather than arbitrary numbers: canvas 0, cue and depth ruler
4, panels and timeline 5, top bar and map key 6. Transparent WebGL geometry has its own explicit
`ORDER` table in `OceanScene.ts`, because Three.js sorts by centroid and that is meaningless for
world-spanning geometry (ADR 0006).

## Components

Shape vocabulary: `12px` for a panel, `8px` for a button or a callout, `6px` for a form control,
`4px` for a segment, `999px` for a pill, `50%` for an icon button. Focus is always
`2px solid var(--primary)` at `2px` offset, globally, never per component.

- **Primary button** (`.dive`) - solid accent fill, `on-primary` ink, 8px radius, 34px tall on
  the top bar. The arrow moves on hover; the button does not lift. Disabled is `opacity: 0.45`
  with the cursor reset, never a colour change.
- **Ghost button** - `surface-low` fill, `outline` border, same 34px height. Every control on the
  top bar is 34px, set once, because three buttons on three different baselines is what happens
  otherwise.
- **Icon button** - a 34px circle. Hover tints to `--primary` and lifts 1px.
- **Bay** - 344px left, 348px right, flush to the edge of the glass, `--frame` opaque, square,
  one `--frame-rule` on the inner edge and one along the bottom so a short bay is still a closed
  shape. Scrolls with a **pure-CSS scroll cue**: two `local` gradient layers that scroll with the content and two `scroll` shadows pinned
  to the frame, so a shadow appears at an edge exactly when there is content past it, with no
  measurement to fall out of step. `scrollbar-gutter: stable both-edges` - measured, it costs no
  height and buys a panel that is not lopsided.
- **Control group** - a header button plus a body, independently collapsible, with a neutral
  caret drawn from two 1.5px borders. A group is open when its `openGroups` entry is `=== true`,
  never when it is absent. Header padding is `7px 16px`; body padding is `0 16px 9px`. The
  **first group is the primary bay** - a tinted `--frame-inset` ground and a 15px name - because
  the Variable selector decides what the water is and is not one row of ten.
- **Segmented control** - a wrapping 2-column grid whose 1px gaps over a coloured ground draw the
  dividers, so it wraps to any number of items with no last-child rule to get wrong. The active
  segment is **filled**, not tinted, so it reads at a glance.
- **Slider** - 3px track, 14px accent thumb with a `--primary-wash` halo that grows on hover.
  Label left, live value right in mono, on a shared baseline.
- **Readout** - mono, `--primary`, sits on the group header so a closed group still reports its
  value. This is the component that makes a collapsed panel usable.
- **Note** (`.note`) - the small caveat under a control. Currently a left stripe; see Don'ts.
- **Map key** - names everything drawn on the water, folds, drags, remembers its position, and
  **swaps entirely** for the bias map's scale when the dots stop meaning "an instrument".

Every interactive element has default, hover, focus-visible and active. Anything clickable is a
real `<button>`.

## Do's and Don'ts

**Do**

- Give every new control a `guide.ts` entry and a tour step. Two probes fail without them, and an
  unexplained control is worse than no control.
- Put *what* and *how much* on the left panel, and *why* on the guide panel. Never both in both.
- Let a group's readout carry its value, so a collapsed group still reports.
- Measure a neighbour rather than assuming its size, and measure the dimension you need - a
  hidden panel still returns a rect and it is all zeros.
- Check both themes. Every time.
- Fill a figure from the bake through a `{token}`, and let an unfilled token take its whole
  sentence off the screen rather than print a number from a bake that is gone.
- Grep the whole of `src/` for a class before deleting its rules. Nothing compiles CSS against
  its markup here, and `.guide-body` was already lost that way once.

**Don't**

- **Side stripes.** `border-left` over 1px as a coloured accent. All eight are gone - six in
  `styles.css` and two on the landing page - and each replacement kept what the colour was
  carrying rather than merely dropping the border: `.verdict` moved its three tones onto a lead
  mark, and the two caveats kept their amber and gained the literal word "Caveat", which survives
  being read across an exhibition room in a way a 2px edge does not. `.disclosure` and
  `.mapkey-fold` are CSS triangles, not stripes.
- **An eyebrow above every section.** The landing page had one above seven of seven; all seven are
  gone and the hero's stays, because it is problem-statement metadata rather than a kicker.
- **Uppercase tracked mono as a default.** It is a wordmark treatment and a unit treatment. It is
  not how a group is named, a legend is titled, a chart is captioned or a status is reported.
- **Decorative blur.** There is none left in the chrome. A new one needs an argument that opacity
  cannot answer.
- **Hue alone.** The model curve is dashed as well as grey; a verdict tone is paired with words.
- **Hiding a control instead of resetting it.** `selectField()` is the only place that may turn
  something off. Hiding a checkbox while its state stays on leaves a reader with a layer they
  cannot remove.
- **A palette chooser.** A palette belongs to a Field. ADR 0010 deleted the last one.
- **Em dashes.** Plain hyphens, everywhere, including in code comments.
- **Backticks inside a GLSL template literal.** They end the string and the error points two
  lines away.
