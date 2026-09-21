# SIH 2026 prototype video - script, version 1 (the video already recorded)

> **Superseded on 2026-09-20 by [`script.md`](script.md).** Kept because it is what the recorded
> video says, word for word. Several sentences here are now known to be wrong - "the model
> assimilates Argo observations", "the seventeen moored buoys it did not use", "five and a half
> times" (not like for like: buoys are compared to 500 m, floats to about 2000 m) - and the
> counts are from an older bake. Do not copy from this file. Re-record from `script.md`.
>
> **The product name and the link in this file were updated on 2026-09-20 and the recording was
> not.** The audio still speaks the old name in its closing line, and the old link 404s. That is
> a second reason the video has to be re-recorded, not a transcription error here.

**How to read this page.**

Plain text is what you say out loud. Read it as written.

> **On screen ·** Indented, quoted lines are what you do. Never spoken. Every one names a real
> control, so you never have to guess what to click.

**Length: 850 spoken words**, counted from this file - 801 until the 2026-09-07 pass, which added
49 by trading eleven claims for more careful ones. That is **5:19 at a brisk 160 words a minute**
or **5:40 at a comfortable 150**, plus the marked silences. Expect **about 5:50 on the recording**,
which leaves room to slow down on the numbers.

**Numbers are written the way they are said**, because this page is read aloud: "twenty-six
degrees", not "26 degrees". The one figure that resists it is the Argo floats' 0.18 degC, which
cannot be spelled out without either a decimal or a rounding that makes the sentence false - a
quarter of a degree is the all-instrument figure and gives 4.2x, not 5.5 - so that sentence names
the floats instead of restating the number.

**The audience is not technical.** A judge watching this may never have opened an ocean model.
Nothing here needs a science background to follow, and no sentence uses a term the picture on
screen has not already shown.

**Every number spoken here is in [`FACTS.md`](FACTS.md)**, generated from the running build. If a
figure has moved, re-run `collect_facts.py` and correct the sentence before you record.

---

## Before you press record

1. Open **https://rak2315.github.io/oceanverity/app.html** and let it finish loading. It settles
   on the spinning globe with India facing you.
2. Press **F11** for full screen, so no browser chrome is in the recording.
3. In the left panel, close every group except **Variable**.
4. Record at **1920 x 1080**.
5. Rehearse the dive twice. It is the most important moment in the video.

**Two words to say carefully.** **Thermocline** is "THERM-oh-cline". **Argo** is "AR-go" - it is
the name of the international float programme, not an acronym.

---

## 0:00 - 0:20 · The hook

> **On screen ·** Open already dived into the water, on the full three-dimensional block, rotating
> slowly. No panels. Let it turn for two seconds in silence before the first word.

India runs a computer model of the ocean around it. It feeds cyclone warnings, search and rescue,
and the advisories that tell fishermen where to go.

There are also two hundred and fifty-nine Argo floats represented here, collecting real
measurements from that same water.

The gap was not a lack of data. It was the lack of one interactive, depth-resolved view that put
the model and measurements together.

> **On screen ·** Hold one more beat on the rotating water before cutting away.

---

## 0:20 - 0:55 · The problem

> **On screen ·** Cut to the opening globe view. Reload `app.html` and do **not** press "Dive into
> the water". You will see the sphere with the Indian Ocean region coloured on it.

This is closer to the traditional workflow: a map of the ocean, often viewed one variable and one
depth at a time.

> **On screen ·** Press play at the left of the timeline along the bottom. Let the thirty-six analyses
> run so the colours visibly change. Leave it playing through the next lines.

The model output and float measurements are often handled through separate tools or workflows.
Both draw the ocean the same way - flat, and one depth at a time.

So the question that actually matters has no tool behind it. Not "what does the model say", because
it always says something. The question is: **is the model right - here, at this depth, today?**

> **On screen ·** Press play again to pause. Let the map sit still.

If that model has drifted from reality in the Bay of Bengal, **you want to know before the cyclone,
not after.**

---

## 0:55 - 1:55 · The dive, and the comparison

**The heart of the video. Do not rush it.**

> **On screen ·** Click "Dive into the water", top right. Let the whole camera move play out. Do
> not cut it short.

Let me fly into it.

> **On screen ·** Drag slowly across the water once, so the viewer sees it is genuinely
> three-dimensional.

That is the Indian Ocean as one solid body of water. **Five metres down to two kilometres, all at
once.**

That sharp band is the thermocline - the transition between the warm surface layer and the colder
deep ocean. The depth of that warm layer matters because it affects how much heat a tropical
cyclone can draw from the ocean.

> **On screen ·** In the Variable group, under "Ocean state", click "Salinity", then "Density",
> then back to "Temperature". Pause about a second on each so the water re-colours.

Saltiness through the same water. Density. **Fifteen variables in total**, and most of them are
worked out here rather than simply passed through.

> **On screen ·** Click one of the white float markers in the top of the water. The comparison
> panel opens on the right. Stop moving the mouse and let the viewer read the chart for two full
> seconds.

But this is the moment that matters. Those white markers are real instruments, drawn where they
actually were on this date. Click one.

**The solid line is what the instrument measured. The dashed line is what the model predicted at
the same location and time, evaluated at the observation depths.** The band between them is the
disagreement.

> **On screen ·** Read the two figures off the panel as they appear - the depths compared and the
> average gap. They move with every re-bake, so say what is on screen rather than a memorised
> number. On the current build a typical float comes out near fifty depths and a gap of a tenth of
> a degree.

Every depth compared, and the gap between them measured.

---

## 1:55 - 2:35 · Why it had to be three-dimensional

> **On screen ·** Click "Set up a cyclone question" at the top of the left panel. The console
> reconfigures in one step and opens on Cyclone Heat Potential.

One press, and the console becomes a cyclone tool. This is the fuel a storm runs on - not surface
warmth, but heat stored down the whole column.

> **On screen ·** Click "Depth of 26 °C". A curved surface appears inside the block.

And this is the one that needs three dimensions.

That surface shows the depth of the twenty-six degree isotherm - a commonly used indicator of how
deep the warm water extends. **Where it bulges downward, the warm layer is deeper**, so a passing
storm cannot churn up cold water to weaken itself.

Look at the central Bay of Bengal. **Here, the warm layer extends deeper** - meaning greater ocean
heat is available to a passing storm.

> **On screen ·** Rotate slowly west, towards Somalia and Oman, where the same sheet rises almost
> to the surface.

Off Somalia and Oman, the same surface rises toward the top, because cold water is being pulled up
from below. **That is a thin lid, not fuel.**

On a flat map, that difference is a number in a table. Here it is a shape you see at a glance.

---

## 2:35 - 3:20 · The currents, and the part we are proudest of

> **On screen ·** Press "Leave cyclone mode". Open the Variable group, click the "Circulation"
> tab, select "Current Speed". Thousands of dots begin flowing. Let them run for three seconds.

Switch to circulation and the ocean starts moving. Those are the real analysed currents.

> **On screen ·** Open "Model vs instruments" and tick "Colour instruments by disagreement". Every
> marker recolours.

Now the honest part.

Across **two hundred and sixty-six instruments**, the typical gap is **about a quarter of a
degree**.

But the model assimilates Argo observations, so agreement with those floats is not a fully
independent test.

Against the **seventeen moored buoys it did not use**, the gap is **just over a degree** - about
**five and a half times** what the Argo floats show.

**We could have shown one flattering average. We show the number that makes us look worse, because
that is the one a forecaster actually needs.**

---

## 3:20 - 4:00 · Why you can believe it

> **On screen ·** Select "Observation Coverage" from the "Evidence" tab. Flat bands show where
> there is no observational data at all.

Same principle here. This view does nothing except show **where nobody has measured anything** -
nine point nine percent of this block has no observational coverage behind it. Most tools quietly
colour that in. **We draw the gap as a gap.**

> **On screen ·** Back to the platform. Once it has loaded, turn the Wi-Fi off on camera if you
> can, then keep clicking float markers. The core demo continues to work because the required
> dataset is already local.

Every figure on this screen can be traced to the public dataset it came from, with the date we
tested it. Nothing is typed in by hand.

Once the platform is loaded, **the demo makes zero external network calls.** The required demo
dataset is shipped with the build, so **a dead venue network cannot kill the demonstration.**

---

## 4:00 - 4:45 · Who it is for

> **On screen ·** Click "Explore" in the top bar. The eight plain-language question cards appear.
> Click one and let it drive the platform.

The problem statement names students and the public too. Fifteen variables is right for a scientist
and wrong for everyone else - so the same platform becomes **eight plain questions**, each carrying
the caveat that simplifying it costs.

> **On screen ·** Return to the platform, back out to the full block of water, and let it rotate
> slowly. This is the last thing on screen.

It runs in a modern browser on a normal laptop, with **no installation or licence required**. So it
can be deployed as a browser-based tool for forecasters without requiring a desktop installation.

It hands its data back out in the standard formats ocean institutes already use, so it fits beside
what they have instead of replacing it. And you can **drag your own data file onto the page** and
see it in the same viewer.

Adding a new data source can be one adapter class. **That is not a promise. That is the
architecture we already built.**

---

## 4:45 - 5:05 · The close

> **On screen ·** Stay on the slowly rotating block of water. Two full seconds of silence before
> the final three lines.

We did not set out to make the ocean look beautiful.

We set out to make it **answerable.**

OceanVerity. Team Sigmoid.

---

## Notes for recording

**The four moments that have to land.** Everything else supports them.

1. **The dive**, around 1:00. Let the transition play in full.
2. **The float comparison**, around 1:40. Stop moving the mouse and let people read the chart.
3. **The twenty-six degree surface bulging downwards**, around 2:10. This is the clearest argument
   in the video for why three dimensions were necessary.
4. **The two disagreement numbers**, around 3:05, and **the wifi coming off**, around 3:50.

Never cut those four. They are the video.

**Pacing.** Say numbers slowly and in full. "Three quarters of a degree", not "point seven five".
"Two hundred and thirty instruments", not "two-thirty".

**Silences.** The two seconds before the first word and before the last three lines are deliberate.
Do not fill them.

**Music.** If you use any, fade it under the opening rotation and out before the first word. No
music bed under the narration.

**If you overrun**, the two places to lose time without losing an argument are the salinity and
density switch at 1:30 - keep the action, drop the sentence - and the last paragraph of "Who it is
for". Together that is about forty words.

**If a live demo makes you nervous**, record the screen actions and the narration separately and
lay the audio over the footage. The actions above are written in order, so they can be captured as
one continuous take.
