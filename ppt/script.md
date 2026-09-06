# SIH 2026 prototype video - script

**Target 4:30 to 5:30.** Read at a normal speaking pace, not fast.

**Normal text is narration.** <span style="color:#888">*Grey italic is the screen action - what
to click, what appears, what the viewer should notice.*</span>

Every number spoken here is in [`FACTS.md`](FACTS.md), which is generated from the build. If a
figure has moved, re-run `collect_facts.py` and fix the sentence before recording.

**Before you record:** open the landing page, let the globe finish loading, then open the
platform in a second tab and let it settle on the globe. Full screen. Rehearse the dive twice -
it is the moment that lands.

---

## 0:00 - 0:20 · The hook

<span style="color:#888">*Open on the platform, already dived in, slowly rotating the block of
water. No panels visible yet. Let it move for two full seconds before the first word.*</span>

> India spends crores running an ocean model.
>
> India also has two hundred and twenty-eight robot floats drifting in that exact same water,
> taking real measurements, right now.
>
> And until this project, **nobody could look at the two together.**

<span style="color:#888">*Hold on the rotating water for a beat after "together".*</span>

---

## 0:20 - 1:00 · The problem, and why it matters

<span style="color:#888">*Cut to a plain flat map - use the globe view of the platform, before
the dive. Then scrub the timeline one step so it visibly redraws.*</span>

> Here is what an ocean forecaster actually has today. The model output opens in one desktop
> program. The float measurements open in another. Both of them draw the ocean the same way -
> **a flat map, one depth at a time.**
>
> So the question a forecaster really has has no tool behind it. Not *"what does the model say"*.
> The real question is: **"is the model right - here, at this depth, today?"**

<span style="color:#888">*Slowly zoom the flat map. Let it look as limited as it is.*</span>

> That matters more than it sounds. This model feeds cyclone forecasts, search and rescue, and
> fishing advisories for the entire Indian coastline. If it is drifting away from reality in the
> Bay of Bengal, **you want to know before the cyclone, not after.**

---

## 1:00 - 1:30 · The core idea, and the USP

> So we built Samudra 3D. And the important thing is what we decided **not** to build.
>
> The problem statement asks for a 3D visualisation. We read it differently. **A picture is not
> the deliverable. The comparison is.**
>
> Anyone can render the ocean and make it look impressive. Our platform does something almost
> nobody does: **it scores the model against reality, and it prints the answer even when the
> answer is unflattering.**

<span style="color:#888">*Cut back to the platform on the globe, panels visible now.*</span>

---

## 1:30 - 2:45 · The prototype, part one: the dive and the comparison

**This is the money shot. Do not rush it.**

<span style="color:#888">*Platform on the globe view, India centred, the study region glowing.
Press "Dive into the water". Let the full camera transition play - do not cut it short.*</span>

> This is INCOIS's own analysis. Let me fly into it.

<span style="color:#888">*The globe opens into the ray-marched block. Rotate slowly once.*</span>

> That is the Indian Ocean as a solid body of water - **five metres down to two kilometres**, all
> of it at once. Not a stack of slices you page through. Warm at the top, cold at the bottom, and
> that sharp colour change in the middle is the thermocline - the layer a cyclone actually feeds
> on.
>
> The white markers are the real instruments, drawn where they actually were on this date.

<span style="color:#888">*Click one Argo float marker. The comparison panel opens on the right.
Pause on it. Let the viewer read the chart.*</span>

> Now - click one.
>
> **Solid line is what the instrument measured. Dashed line is what the model predicted.** Same
> water, same day, same depths. And the band between them is the disagreement.
>
> Fifty-four depths compared. Average gap: **zero point zero eight degrees.**

<span style="color:#888">*Point at the verdict line with the cursor.*</span>

> That is the whole product in one click. Not a prettier picture of the model - **a number on how
> far the model sits from the truth.**

---

## 2:45 - 3:30 · The prototype, part two: the honesty

<span style="color:#888">*Open "Model vs instruments" in the left panel. Turn on "Colour
instruments by disagreement". The markers recolour across the basin.*</span>

> And we do that for every instrument at once.
>
> Across **two hundred and thirty instruments**, the typical gap is **zero point one nine
> degrees.** Which sounds excellent.
>
> But here is the part I am proud of. INCOIS *feed* the Argo floats into their model. So a float
> agreeing with the model is largely the model agreeing with itself. The honest test is the **nine
> moored buoys they do not feed in** - and against those, the gap is **zero point seven five
> degrees. Four times worse.**
>
> We print both numbers, separately, on screen. **We could have shown you one flattering average.
> We show you the one that makes us look worse, because that is the number a forecaster actually
> needs.**

<span style="color:#888">*Switch the variable to "Observation coverage". The map shows the gaps
where nobody measured.*</span>

> Same principle here. This variable does nothing except show you **where nobody has measured
> anything.** Nine point nine percent of this ocean has no observation behind it at all. Most
> tools quietly colour that in. We draw the gap **as a gap.**

---

## 3:30 - 4:00 · Built for the people who need it

<span style="color:#888">*Press "Set up a cyclone question". The whole console reconfigures in one
step.*</span>

> One press, and the platform becomes a cyclone tool - heat potential, the depth of the
> twenty-six degree layer, how far the wind has stirred. **The fuel a storm runs on.**

<span style="color:#888">*Open Explore. Show the eight question cards. Click one and let it run.*</span>

> And because the problem statement names students and the public too, there is a second door.
> **Fifteen variables is right for a forecaster and wrong for a school group** - so the same
> platform becomes eight plain questions, each carrying the caveat that its simplification costs.
> There is a kiosk mode for exhibition screens too.

---

## 4:00 - 4:45 · How it actually works, and why it is real

<span style="color:#888">*Open provenance.html. Scroll it slowly. Then open requirements.html and
click one clause link, showing it open the platform on that control.*</span>

> Underneath: **nine source adapters** pulling from INCOIS's ERDDAP, Argo, Copernicus, NOAA - all
> public, all live, all listed here with the date we tested each one.
>
> Python does the science, and **all of it is tested - three hundred and seventy-seven tests**,
> because a wrong constant in an ocean formula gives you a number that is smooth, plausible, and
> completely false.
>
> The browser does the rendering, in WebGL, with no plugin and no install.

<span style="color:#888">*Point at the architecture. Then back to the platform, disconnect wifi
visibly if you can, and keep clicking.*</span>

> And one rule shapes everything. **The rendered picture is compressed for the graphics card, so
> we never read a number off it.** Every figure a user sees comes from the full-precision grid
> instead. The picture is for your eyes. The numbers come from the data.
>
> One more thing - **this makes zero network calls to run.** Watch.

<span style="color:#888">*Turn wifi off. Keep clicking floats. Everything still works.*</span>

> The whole dataset ships inside the build. **A dead venue network cannot kill this demo.**

---

## 4:45 - 5:20 · Impact, scale, and the close

<span style="color:#888">*Back out to the full block of water. Slow rotation. Let it be the last
thing on screen.*</span>

> Where this goes. It runs in any browser on any laptop, so INCOIS could put it in front of
> forecasters tomorrow with no procurement and no installs. It already serves its data back out
> through **OPeNDAP, CF NetCDF and OGC WMS** - the three standards ocean institutions already
> speak - so it plugs into what they have rather than replacing it. And you can **drop your own
> NetCDF file onto the page** and it renders in the same viewer, which means the next dataset
> does not need us.
>
> Adding a new data source is one Python class. Adding a new variable is one function. That is
> not a promise - **that is the architecture we already built.**

<span style="color:#888">*Hold on the water. Two seconds of silence before the last line.*</span>

> We did not set out to make the ocean look beautiful.
>
> We set out to make it **answerable.**
>
> Samudra 3D. Team Sigmoid.

---

## Notes for recording

- **Do not read this like a list of features.** Every feature shown is there to prove one claim:
  the comparison is the product.
- **The three moments that must land:** the dive at 1:30, the two residual numbers at 3:00, and
  the wifi going off at 4:30. Everything else supports those.
- **Slow down on numbers.** Say "zero point seven five degrees", not "point seven five".
- **The two-second silences are deliberate.** Before the first word, and before the last line.
- **Screen recording at 1920x1080**, platform full screen, browser chrome hidden.
- **Do not add a music bed under the narration.** If you want music, fade it under the opening
  rotation and out before the first word.
- If you overrun, cut from **3:30 - 4:00** (cyclone mode and Explore) first. It is the only
  section that is breadth rather than argument.
