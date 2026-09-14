/**
 * The Cyclone Montha walkthrough, measured.
 *
 * A storm case is exactly the feature that looks right and says something wrong, so this checks
 * what it says as well as what it draws:
 *
 *   1. **Every step sets up what its card claims** - the Field, the analysis date, the buoy, the
 *      drift pin - checked against a table written here, not read from `cases.ts`, so a step
 *      that stopped doing its job cannot pass by agreeing with itself.
 *   2. **Every figure on a card comes from `montha.json`.** Each number in a card's text must be
 *      one the probe can derive from the file. A number typed into a caption fails.
 *   3. **IMD's track is drawn while the walkthrough is open and not after it.** A frame pair that
 *      differs only in the line's `visible`, and the line's vertex count against the file.
 *   4. **Touching a control ends it**, like the tour.
 *
 *   node probe-case.mjs        (needs a preview server on 4173)
 */
import { chromium } from "playwright";
import { comparePixels, decodePng } from "./probe-pixels.mjs";

const SERVER = process.env.PREVIEW_URL ?? "http://localhost:4173";

const problems = [];
const browser = await chromium.launch({
  args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
const page = await browser.newPage({ viewport: { width: 1400, height: 800 } });
page.on("pageerror", (e) => problems.push(`pageerror: ${e.message}`));
page.on("console", (m) => m.type() === "error" && problems.push(`console: ${m.text()}`));

const stormCase = await (await fetch(`${SERVER}/data/cases/montha.json`)).json();
const { before, after } = stormCase.steps;
const buoy = stormCase.buoys[0];

/** What each step must have arranged. Independent of `cases.ts` on purpose. */
const PROMISED = [
  (s) => s.fieldKey === "temperature" && s.timestepIndex === before,
  (s) => s.fieldKey === "heat_potential" && s.timestepIndex === before,
  (s) => s.fieldKey === "d26" && s.timestepIndex === before,
  (s) => s.fieldKey === "heat_potential" && s.timestepIndex === after,
  (s) => s.fieldKey === "temperature" && s.timestepIndex === after,
  (s) => s.fieldKey === "temperature" && s.timestepIndex === after && s.selectedFloatId === buoy.id,
  // The pin has to draw a line: a pin on a cell with no current draws nothing, which passed once.
  (s) => s.fieldKey === "current_speed" && s.timestepIndex === after && s.driftPin !== null && s.driftDrawn,
];

/** Every number a card may print, in the forms the card prints them. */
function allowedNumbers() {
  const out = new Set();
  const add = (value) => {
    const n = Math.abs(Number(value));
    if (!Number.isFinite(n)) return;
    for (const text of [String(n), n.toFixed(0), n.toFixed(1), n.toFixed(2)]) out.add(text);
  };
  const walk = (value) => {
    if (typeof value === "number") add(value);
    // Ids and IMD's own text carry figures too: a buoy id, the landfall day.
    else if (typeof value === "string" && !/^\d{4}-\d{2}-\d{2}T/.test(value)) (value.match(/\d+(?:\.\d+)?/g) ?? []).forEach(add);
    else if (Array.isArray(value)) value.forEach(walk);
    else if (value && typeof value === "object") Object.values(value).forEach(walk);
  };
  walk(stormCase);
  for (const change of Object.values(stormCase.changes)) {
    for (const band of [change.near, change.far]) add(band.medianAfter - band.medianBefore);
  }
  // Derived on the card, each from the file: days from the "before" analysis to formation, the
  // peak wind in km/h to the nearest 5, and the day of the month of each date shown.
  add(Math.round((Date.parse(stormCase.formed) - Date.parse(stormCase.steps.beforeTime)) / 86400000));
  add(Math.round((stormCase.peakWindKt * 1.852) / 5) * 5);
  for (const stamp of [stormCase.formed, stormCase.steps.beforeTime, stormCase.steps.afterTime]) {
    add(new Date(stamp).getUTCDate());
  }
  add(new Date(stormCase.formed).getUTCFullYear());
  add(26); // the isotherm the sheet is drawn at: a definition, not a measurement
  return out;
}
const ALLOWED = allowedNumbers();

await page.goto(`${SERVER}/app.html?case=montha`, { waitUntil: "load", timeout: 60000 });
await page.waitForFunction(() => !!window.__store?.getState().stormCase, null, { timeout: 120000 });
await page.waitForSelector(".tour.case", { timeout: 60000 });
await page.waitForTimeout(6000);

const steps = await page.evaluate(() => document.querySelector(".tour-count")?.textContent ?? "");
const count = Number(/of (\d+)/.exec(steps)?.[1] ?? 0);
if (count !== PROMISED.length) problems.push(`card says ${count} steps, this probe checks ${PROMISED.length}`);

for (let index = 0; index < count; index++) {
  await page.evaluate((i) => window.__store.setState({ caseStep: i }), index);
  // Polled, not a fixed wait: a step's data (the current files behind a drift line) arrives in
  // the background, and under software rendering on a loaded machine that took longer than a
  // fixed 2.5 s and failed a correct step. A minute is the limit; a step still wrong then is wrong.
  const read = () => page.evaluate(() => {
    const s = window.__store.getState();
    const card = document.querySelector(".tour.case");
    return {
      fieldKey: s.fieldKey,
      timestepIndex: s.timestepIndex,
      selectedFloatId: s.selectedFloatId,
      driftPin: s.driftPin,
      caseStep: s.caseStep,
      driftDrawn: !!window.__scene.driftLine?.visible,
      text: card ? [...card.querySelectorAll(".tour-title, .tour-body, .case-note")].map((e) => e.textContent).join(" ") : "",
    };
  });
  let landed = await read();
  for (let waited = 0; waited < 60000 && !PROMISED[index]?.(landed); waited += 1000) {
    await page.waitForTimeout(1000);
    landed = await read();
  }
  const title = landed.text.slice(0, 60);
  if (landed.caseStep !== index) problems.push(`step ${index + 1} closed itself or moved on (caseStep ${landed.caseStep})`);
  if (!PROMISED[index]?.(landed)) problems.push(`step ${index + 1} "${title}" did not set up what it claims: ${JSON.stringify({ ...landed, text: undefined })}`);
  const numbers = landed.text.match(/\d+(?:\.\d+)?/g) ?? [];
  const typed = numbers.filter((n) => !ALLOWED.has(n));
  if (typed.length) problems.push(`step ${index + 1} "${title}" prints numbers not in montha.json: ${typed.join(", ")}`);
  console.log(`step ${index + 1}: ${title} ... ${numbers.length} figures, ${typed.length} unexplained`);
}

// ---- 3. the track -----------------------------------------------------------------------
const line = await page.evaluate(() => {
  const object = window.__scene.stormLine;
  return {
    visible: object?.visible,
    vertices: object?.geometry.getAttribute("lonLat")?.count ?? 0,
    fixes: window.__scene.stormFixes?.visible ? window.__scene.stormFixes.geometry.getAttribute("lonLat").count : 0,
    floatTracks: window.__scene.trackLines?.visible,
  };
});
if (line.fixes !== stormCase.track.length) problems.push(`${line.fixes} track dots drawn, IMD recorded ${stormCase.track.length} positions`);
if (line.floatTracks) problems.push("float tracks are still drawn over the storm track");
// Five parallel copies of every segment: WebGL lines are one pixel, so the track is drawn thick.
const expected = (stormCase.track.length - 1) * 2 * 5;
console.log(`storm line: visible ${line.visible}, ${line.vertices} vertices against ${expected} from the file`);
if (!line.visible) problems.push("IMD's track is not drawn while the walkthrough is open");
if (line.vertices !== expected) problems.push(`the drawn track has ${line.vertices} vertices, the file implies ${expected}`);

// Frame pair on `visible` alone. Back to step 1, where nothing else is moving.
await page.evaluate(() => window.__store.setState({ caseStep: 0 }));
await page.waitForTimeout(3000);
const withTrack = await page.screenshot({ timeout: 180000 });
await page.evaluate(() => { window.__scene.stormLine.visible = false; window.__scene.stormFixes.visible = false; });
await page.waitForTimeout(500);
const withoutTrack = await page.screenshot({ timeout: 180000 });
await page.evaluate(() => { window.__scene.stormLine.visible = true; window.__scene.stormFixes.visible = true; });
const pair = comparePixels(decodePng(withTrack), decodePng(withoutTrack));
console.log(`track on against off: ${pair.count} px`);
// A hairline polyline: the question is drawn or not drawn, as in probe-drift.mjs.
if (pair.count < 40) problems.push(`the storm track changes only ${pair.count} px, so it is not really drawn`);

// ---- 4. touching a control ends it, and the track goes with it --------------------------
await page.evaluate(() => window.__store.getState().set("touched", "timestep"));
await page.waitForTimeout(1000);
const after4 = await page.evaluate(() => ({
  caseStep: window.__store.getState().caseStep,
  visible: window.__scene.stormLine.visible,
  card: !!document.querySelector(".tour.case"),
}));
if (after4.caseStep !== null || after4.card) problems.push("touching a control did not end the walkthrough");
if (after4.visible) problems.push("IMD's track stayed on the water after the walkthrough ended");

await browser.close();
if (problems.length) {
  console.log(`\n${problems.length} problem(s):`);
  for (const p of problems) console.log(`  - ${p}`);
  process.exit(1);
}
console.log("\nthe walkthrough keeps every promise");
