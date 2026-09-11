# Derivable quantities become Variables; the palette chooser goes

The Colourbar was a dropdown of nine cmocean palettes sitting directly under the Variable
selector. Seven of them named quantities the platform does not carry. Choosing "dense - Density"
drew the temperature field in the colours of density, under a printed warning that the colours
would "not carry their usual meaning". A presentation control was reading as a data control, and
the warning was an admission rather than a fix.

## What we did

Split the nine by whether the quantity behind them is real, derivable, or neither.

| Palette | Quantity | Outcome |
| --- | --- | --- |
| `thermal`, `haline` | Temperature, Salinity | Already Fields. Now bound to them. |
| `coverage` | Observation Coverage | Already a Field. Removed from the chooser, where it was a duplicate of its own button. |
| `dense` | Density | **Became a Field.** TEOS-10 sigma-theta from temperature, salinity and pressure. Exact, no download. |
| `balance` | Anomalies about zero | **Became a Field.** Departure from the mean of the baked steps. |
| `delta` | Differences | Deleted. A second diverging scale with nothing to sit on. |
| `algae` | Chlorophyll | Deleted. Biological and optical; needs BGC-Argo or satellite ocean colour, and either would be a 2-D surface layer rather than a Volume. |
| `oxy` | Dissolved oxygen | Deleted. The only complete gridded field for this region is a decadal climatology with no date, which cannot share a ten-day 2026 timeline. Deriving it from T/S regressions would be inventing data. |
| `deep` | Bathymetry | Deleted. GEBCO is a download, not a derivation, and the sea floor is scenery rather than a variable. |
| `speed` | Current speed | Deleted. See below. |

What is left is one palette per Field, named in the `FieldSpec`. A Field and its colours cannot
be separated, so there is no mismatch left to warn about and no chooser to make one. The
colourbar swatch, the band key and the range sliders stay: those do analytical work.

This is also the answer to the part of PS 26067 that asks for additional model variables "with
minimal code change". Density and the anomaly ride the existing bake, encoder, manifest and
shader. Neither needed a line of GLSL.

## Why current speed is not among them

It is the one the problem statement names, so it was prototyped rather than dismissed:
geostrophic velocity by thermal wind from the new density field, integrated from a reference
level of no motion at 1000 dbar, the Argo parking depth.

It does not blow up at the equator - the Grid's rows sit at half degrees, so `f` never reaches
zero - and every value it produces is finite and plausible. That is the problem. Measured on
2026-07-30, at the height of the southwest monsoon:

| Region | Prototype | Reality |
| --- | --- | --- |
| Somali Current, 5-11 N | max **0.16 m/s** | 1.5-2.5 m/s, the Great Whirl |
| Equatorial band, 2 S to 2 N | max **1.90 m/s** | ~0.5-1 m/s, and geostrophy does not hold here at all |
| Bay of Bengal interior | 0.08 m/s median | 0.1-0.3 m/s |
| Arabian Sea interior | 0.05 m/s median | 0.1-0.3 m/s |

So the field is wrong by more than a factor of ten at the fastest current in the region, in the
month it is fastest, and puts the fastest water in the block in the one place the method is
guaranteed not to apply. A 1 degree analysis smooths away the density gradients that drive a
western boundary current, and "no motion at 1000 m" is false underneath one.

A blank band would have been survivable. A calm Somalia and a racing equator is worse, because
it is plausible: it invites a viewer to believe it, and the first person to look for the Somali
Current would find it missing.

INCOIS's own `incois_valueadded_products_datasets` publishes GEO_U and GEO_V, properly derived
and validated. That series stops in March 2019 against an analysis running to July 2026, so it
cannot share this timeline. It remains the right source if currents are ever added, on their own
clearly dated view.

## The sixth Field, when there is one

TCHP - heat integrated from the surface to the 26 degC isotherm - is exact, uses only the
temperature Grid already on disk, and is the quantity that governs cyclone rapid intensification.
It is a column integral rather than a volume, so it needs a rendering decision the other derived
Fields did not, which is the only reason it is not here already.

---

## Amended on 2026-09-01: the sixth Field arrived, and so did the log scale

Two things this record left open have been closed. Neither reverses it.

**TCHP is built, along with four more.** The paragraph above says it needs a rendering decision
the other derived Fields did not, and that is exactly what held it up: it is a column integral,
not a volume. The decision is in **ADR 0014** - a column total is draped on the sea surface and a
Field whose value is a depth is drawn as a sheet at that depth - and five hazard Fields arrived
together on the back of it. Each has its own palette, its own guide entry and its own isosurface
meaning, which is what this ADR required of any new Field.

**The log scale is built.** `CONTEXT.md` recorded flatly that "there is no log scale - it warped
the water while the colourbar stayed linear, so the legend became a lie". Reread, that is a bug
report and not a design decision: the shader applied a curve and the swatch beside it did not.

There is now exactly one curve, in `web/src/transfer.ts`, exported both as a TypeScript function
and as the GLSL string the ray marcher inlines. The colourbar gradient is drawn by sampling the
palette through the same function, so the bar visibly bunches its colours towards the low end
when the scale is logarithmic, and a reader matching a colour to a number gets the same answer
from both. It is offered only where the Field's encoded range never goes below zero - there is no
logarithm of a negative number, and bending one half of a diverging scale would move its midpoint
off the value that means "no departure", which is the one thing ADR 0007 exists to protect.

**The palette chooser stays gone.** Five palettes were added in this round - `deep`, `amp`,
`speed`, `tempo`, `matter` - and every one of them arrived attached to a `FieldSpec` and to
nothing else, which is the rule this record set.

---

## Amendment, 2026-09-07: the chooser comes back, and the rule it broke does not

**The colourbar can be switched again.** Every Field offers its own palette plus three or four
alternates, in the Colourbar group.

This record deleted a chooser and was right to. It is worth being exact about **which** part was
wrong, because the two are easy to confuse and only one of them is a design principle.

The dropdown offered nine palettes and **seven of them named quantities this platform does not
carry**. Picking `algae` recoloured temperature in the colours of a chlorophyll measurement nobody
had taken; `oxy` did the same for dissolved oxygen. There was a warning line under the control
admitting the colours meant nothing, which is the shape of a defect rather than a feature. The
failure was **a palette naming a quantity**. It was not **a reader having a choice**.

So the choice is back with the first half kept whole, and four constraints hold it there:

1. **An alternate is labelled by the colours it contains, never by an ocean variable.** The
   buttons read "Navy to yellow", "Black to white", "Navy, white, purple". `PALETTE_LOOKS` in
   `web/src/palette.ts` is that list, and it was read off the shipped tables at positions 0, 128
   and 255 rather than written from memory. Nothing in the interface offers "chlorophyll" as a
   way of drawing temperature, which is the whole of what this ADR threw out.

2. **A diverging Field is only ever offered diverging alternates, and the reverse.** `isDiverging`
   decides which a Field is from its range crossing zero - never from its palette name - and a
   diverging Field's midpoint is a real value: the ray marcher draws two isosurface skins about it
   and the panel prints a `±`. A sequential ramp in its place would put the pale part of the scale
   at an arbitrary number and quietly break the reading. ADR 0007's rule that a midpoint means
   something is what this protects.

3. **A banded palette is offered nothing at all.** Observation Coverage is four flat bands whose
   edges sit at whole cast counts, with a key beside it that names them. A gradient in its place
   repaints every cell holding 1, 2 or 3 casts as "4 or more casts" - the exact bug the log scale
   already shipped once, measured and written up in `transfer.ts`.

4. **One lookup, not two.** `store.activePalette()` is the only answer to "which colourbar is on
   screen", and the GPU texture, the pushed `ViewState`, the colourbar swatch, the vertical
   section and the guide panel all go through it. A second copy disagreeing with the first is
   precisely what got the log scale cut the first time round, and it is the standing rule in
   `styles.css`.

**Five palettes were added to carry it** - `ice`, `gray`, `delta`, `curl`, `diff` - and unlike the
nine this record deleted, none of them names a quantity. `gray` earns its place twice over: it is
the one ramp that survives being projected badly or photocopied, and the one a reader who cannot
separate two of the others can still read.

**`probe-palette.mjs` holds all four constraints**, and it was made to fail on purpose before it
was kept: with the legend pointed at the Field's own table while the water drew the chosen one,
and with the override left to leak across a Field switch, it reported a channel spread of 149 on a
grey ramp and named the leak. Its first draft passed both of those, which is why the ritual exists.

**What has not changed:** a palette still belongs to a Field. `FieldSpec.palette` is still the
default and still the thing `selectField` resets to, exactly as it resets `emphasis`, `scale` and
`isoEnabled` - a chosen colourbar that survived a Field switch would be a hint leaking forwards,
which is a bug this project has fixed three times in other clothes.
