/**
 * "Show me around" walks every control, and does not break on the way.
 *
 * The tour's claim is that a teammate who has never opened this can press one button and be
 * shown the whole console. That is the kind of claim that is true the day it is written and
 * quietly false a round later, when a control is added and nobody remembers the tour exists.
 * So it is measured, three ways:
 *
 *   1. **Coverage.** Every entry in `GUIDE` is named by some step's `covers`. The answer comes
 *      from the shipped module - `tourCoverage()` - not from a list typed into this file.
 *
 *   2. **It survives.** Every step is opened in order and the tour is still open afterwards.
 *      Some store actions end the tour on purpose when a *user* presses them; a step that
 *      presses one on the user's behalf has to put it back, and that is easy to get wrong.
 *
 *   3. **Each step does something.** A step that changes nothing is a caption, and a caption
 *      pretending to be a demonstration is worse than no step. Each one is checked for a real
 *      change in the state the scene reads.
 *
 *   4. **Touching a control pauses it.** The card stays with End and Continue, the scene is left
 *      alone, Continue restores the step and End closes it - including cyclone mode, whose own
 *      action used to end the tour.
 *
 * Console errors and page errors fail it too: a step driving the store into a state no panel
 * expects is exactly the sort of thing that throws in a corner nobody watches.
 *
 *   node probe-tour.mjs        (needs a preview server on 4173)
 */
import { chromium } from "playwright";

const SERVER = process.env.PREVIEW_URL ?? "http://localhost:4173";

const problems = [];
const browser = await chromium.launch({
  args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
const page = await browser.newPage({ viewport: { width: 1400, height: 800 } });
page.on("pageerror", (e) => problems.push(`pageerror: ${e.message}`));
page.on("console", (m) => m.type() === "error" && problems.push(`console: ${m.text()}`));

await page.goto(`${SERVER}/app.html`, { waitUntil: "load", timeout: 60000 });
await page.waitForFunction(() => !!window.__store?.getState().manifest, null, { timeout: 120000 });
await page.waitForSelector("button.dive", { timeout: 60000 });
await page.waitForTimeout(3000);

// ---- 1. every control is covered ---------------------------------------------------------
const coverage = await page.evaluate(() => window.__tour.tourCoverage());
console.log(`tour covers ${coverage.covered.length} of the guide's entries`);
if (coverage.missing.length) {
  problems.push(
    `${coverage.missing.length} controls have a guide entry and are never shown by the tour: ` +
      coverage.missing.join(", "),
  );
}

// ---- 2 and 3. every step opens, changes something, and leaves the tour running -----------
const total = await page.evaluate(() => window.__tour.buildTour(() => {}).length);
console.log(`${total} steps in ${await page.evaluate(() => new Set(window.__tour.buildTour(() => {}).map((s) => s.chapter)).size)} chapters`);

let previous = null;
for (let index = 0; index < total; index++) {
  await page.evaluate((i) => window.__store.setState({ tourStep: i }), index);
  // Long enough for a Field switch to fetch its Volume under software rendering, and for the
  // one step that selects an Anomaly Feature on a timer.
  await page.waitForTimeout(1400);

  const snapshot = await page.evaluate(() => {
    const s = window.__store.getState();
    return {
      tourStep: s.tourStep,
      title: window.__tour.buildTour(() => {})[s.tourStep ?? 0]?.title ?? "?",
      state: JSON.stringify({
        fieldKey: s.fieldKey,
        timestepIndex: s.timestepIndex,
        depthFrom: s.depthFrom,
        depthTo: s.depthTo,
        windowMin: s.windowMin,
        windowMax: s.windowMax,
        isoEnabled: s.isoEnabled,
        volumeEnabled: s.volumeEnabled,
        currentStyle: s.currentStyle,
        biasMode: s.biasMode,
        hazardMode: s.hazardMode,
        touched: s.touched,
        selectedFloatId: s.selectedFloatId,
        selectedAnomaly: s.selectedAnomaly,
        driftPin: s.driftPin,
        sectionFrom: s.sectionFrom,
        showFloats: s.showFloats,
        playing: s.playing,
        openGroups: s.openGroups,
      }),
    };
  });

  if (snapshot.tourStep !== index) {
    problems.push(
      `step ${index + 1} ("${snapshot.title}") ended the tour: tourStep is ` +
        `${snapshot.tourStep} rather than ${index}`,
    );
  }
  if (previous !== null && snapshot.state === previous) {
    problems.push(
      `step ${index + 1} ("${snapshot.title}") changed nothing the scene reads - a step that ` +
        `demonstrates nothing is a caption`,
    );
  }
  previous = snapshot.state;
}

// The card itself has to be on screen at the end, not just the state behind it.
const showing = await page.evaluate(() => !!document.querySelector(".tour .tour-title"));
if (!showing) problems.push("the tour card is not rendered on the last step");

// ---- 4. touching a control pauses the tour, and Continue restores the step ----------------
// Step 9 selects density. The reader switches to salinity by hand.
const densityStep = await page.evaluate(() =>
  window.__tour.buildTour(() => {}).findIndex((s) => s.covers.includes("density")),
);
await page.evaluate((i) => window.__store.setState({ tourStep: i }), densityStep);
await page.waitForTimeout(1400);
await page.evaluate(() => {
  const s = window.__store.getState();
  s.selectField("salinity");
  s.set("touched", "field");
});
await page.waitForTimeout(800);
const paused = await page.evaluate(() => {
  const s = window.__store.getState();
  return {
    tourStep: s.tourStep,
    paused: s.cardPaused,
    fieldKey: s.fieldKey,
    card: !!document.querySelector(".tour.tour-paused"),
    buttons: [...document.querySelectorAll(".tour-paused .tour-actions button")].map((b) => b.textContent.trim()),
  };
});
console.log(`after a touch: ${JSON.stringify(paused)}`);
if (paused.tourStep !== densityStep || !paused.paused || !paused.card) {
  problems.push(`touching a control did not pause the tour: ${JSON.stringify(paused)}`);
}
if (paused.buttons.join("|") !== "End|Continue") problems.push(`paused card offers ${paused.buttons.join(", ")}`);
if (paused.fieldKey !== "salinity") problems.push("the paused tour moved the scene under the reader's hand");

// The hazard mode switch is the one control that used to end the tour through its own action.
await page.evaluate(() => window.__store.setState({ cardPaused: false }));
await page.waitForTimeout(1400);
await page.evaluate(() => window.__store.getState().setHazardMode(true));
await page.waitForTimeout(800);
const hazard = await page.evaluate(() => ({ tourStep: window.__store.getState().tourStep, paused: window.__store.getState().cardPaused }));
if (hazard.tourStep !== densityStep || !hazard.paused) problems.push(`cyclone mode did not pause the tour: ${JSON.stringify(hazard)}`);

await page.click(".tour-paused .tour-actions .primary");
await page.waitForTimeout(1400);
const resumed = await page.evaluate(() => {
  const s = window.__store.getState();
  return { tourStep: s.tourStep, paused: s.cardPaused, fieldKey: s.fieldKey, card: !!document.querySelector(".tour .tour-title") };
});
if (resumed.paused || resumed.tourStep !== densityStep || resumed.fieldKey !== "density" || !resumed.card) {
  problems.push(`Continue did not put the step back: ${JSON.stringify(resumed)}`);
}

await page.evaluate(() => window.__store.getState().set("touched", "opacity"));
await page.waitForTimeout(500);
await page.click(".tour-paused .tour-actions .ghost");
await page.waitForTimeout(500);
const ended = await page.evaluate(() => ({ tourStep: window.__store.getState().tourStep, card: !!document.querySelector(".tour") }));
if (ended.tourStep !== null || ended.card) problems.push(`End did not close the paused tour: ${JSON.stringify(ended)}`);

console.log(problems.length ? `PROBLEMS: ${problems.join(" | ")}` : "clean");
await browser.close();
process.exit(problems.length ? 1 : 0);
