/**
 * The colourbar switcher, measured.
 *
 * ADR 0010 deleted a palette chooser because seven of its nine entries named quantities this
 * platform does not carry, and the amendment that brought a chooser back rests on three claims
 * that are cheap to assert and expensive to notice going wrong:
 *
 *   1. **A Field is offered its own colourbar first, then alternates of its own kind, and never
 *      one of the other kind.** A diverging Field's midpoint is a real value - the ray marcher
 *      draws two isosurface skins about it and the panel prints a `+/-` - so a sequential ramp
 *      in its place would put the pale part of the scale at an arbitrary number. A banded
 *      palette is offered nothing, because a gradient over Observation Coverage repaints every
 *      cell holding 1, 2 or 3 casts as "4 or more casts". Both of those are bugs this project
 *      has already shipped once, through the log scale.
 *   2. **Switching one repaints the water.** A chooser that changes a swatch and not the block
 *      is a control that lies.
 *   3. **The water and the colourbar draw the same table.** This is the standing rule in
 *      `styles.css` and the reason `transfer.ts` has exactly one curve; a second lookup
 *      disagreeing with the first is what got the log scale cut the first time round.
 *
 * And a fourth, because a view you cannot send is half a view: the choice survives the round
 * trip through `currentViewUrl` and `applyDeepLink`.
 *
 *   node probe-palette.mjs        (needs a preview server on 4173)
 */
import { chromium } from "playwright";
import { decodePng } from "./probe-pixels.mjs";

const SERVER = process.env.PREVIEW_URL ?? "http://localhost:4173";
const problems = [];

// What each palette looks like, as `PALETTE_LOOKS` labels them. Written here rather than
// imported so that renaming a label in the app without meaning to fails this probe.
const DIVERGING = [
  "Navy, white, red",
  "Navy, pale yellow, green",
  "Navy, white, purple",
  "Navy, white, olive",
];
const SEQUENTIAL = [
  "Navy to yellow",
  "Indigo to pale yellow",
  "Cream to near-black",
  "Black to pale blue",
  "Black to white",
];
const OWN_LOOK = {
  thermal: "Navy to yellow",
  haline: "Indigo to pale yellow",
  dense: "Pale to plum",
  deep: "Cream to near-black",
  amp: "White to dark red",
  speed: "Cream to dark green",
  tempo: "White to navy",
  matter: "Pale yellow to purple",
  balance: "Navy, white, red",
};

const browser = await chromium.launch({
  args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
let page = await browser.newPage({ viewport: { width: 1400, height: 860 } });
page.on("pageerror", (e) => problems.push(`pageerror: ${e.message}`));

await page.goto(`${SERVER}/app.html`, { waitUntil: "load", timeout: 60000 });
await page.waitForFunction(() => !!window.__store?.getState().manifest, null, { timeout: 120000 });
await page.evaluate(() => document.querySelector("button.dive").click());
await page.waitForFunction(() => window.__store.getState().morph > 0.9, null, { timeout: 120000 });
await page.waitForTimeout(800);

// ---- 1. what each Field is offered -----------------------------------------------------------
//
// The Colourbar group has to be open first: its buttons are not in the DOM while it is shut, and
// a check that reads an empty list every time is a check that passes every time. `probe-hazard`
// learned this about `.colourbar` and read `null` for a round.
const offers = await page.evaluate(async () => {
  const store = window.__store.getState();
  store.set("openGroups", { ...store.openGroups, palette: true });
  // And the alternates within it, which fold: they cost 132 px of a 635 px bay, so they are shut
  // by default and a check that reads them without unfolding reads the one row that is left. The
  // group itself learned this a round earlier and it is the same failure one level in.
  store.set("paletteAlternates", true);
  await new Promise((r) => setTimeout(r, 120));
  const out = [];
  for (const field of store.manifest.fields) {
    store.selectField(field.key);
    await new Promise((r) => setTimeout(r, 40));
    out.push({
      key: field.key,
      own: field.palette,
      // From the range, exactly as `isDiverging` decides it - never from the palette name.
      diverging: field.range[0] < 0 && field.range[1] > 0,
      // `.palette-list`, not `.palette-choice`: the latter now also holds the folded row, which
      // names the colourbar on screen and is not one of the choices.
      choices: [...document.querySelectorAll(".palette-list button")].map((b) =>
        b.textContent.trim(),
      ),
      // The folded row has to report what is actually drawn, or the group's one visible line is
      // a lie while the list is shut.
      folded: document.querySelector(".palette-current")?.textContent.trim() ?? null,
    });
  }
  store.selectField("temperature");
  return out;
});

// The leak, tested by actually leaking one. Reading `paletteOverride` after a plain Field switch
// asserts nothing, because nothing ever set it - a check that can only ever see `null` is a
// check that always passes, which is the whole of `docs/BUGS.md`'s "four probes that could not
// go red". Choose an alternate, switch Field, and require it gone.
const leak = await page.evaluate(async () => {
  const store = window.__store.getState();
  store.selectField("temperature");
  await new Promise((r) => setTimeout(r, 60));
  store.set("paletteOverride", "gray");
  await new Promise((r) => setTimeout(r, 60));
  const chosen = window.__store.getState().paletteOverride;
  window.__store.getState().selectField("salinity");
  await new Promise((r) => setTimeout(r, 60));
  const afterSwitch = window.__store.getState().paletteOverride;
  window.__store.getState().selectField("temperature");
  return { chosen, afterSwitch };
});
console.log(`
  chose ${leak.chosen}, then switched Field: override is now ${leak.afterSwitch}`);
if (leak.chosen !== "gray") problems.push("choosing an alternate did not take");
if (leak.afterSwitch !== null) {
  problems.push(`the override ${leak.afterSwitch} survived a Field switch`);
}

for (const offer of offers) {
  const want = offer.diverging ? DIVERGING : SEQUENTIAL;
  const got = offer.choices;
  // A Field whose own palette is not itself an alternate gets one extra button. That is the
  // design; asserting a fixed count instead called five correct Fields broken.
  const strays = got.filter((c) => !want.includes(c) && c !== OWN_LOOK[offer.own]);
  const ok =
    offer.key === "coverage"
      ? got.length === 0
      : got.length >= 4 && got[0] === OWN_LOOK[offer.own] && strays.length === 0;
  console.log(
    `  ${ok ? "ok  " : "FAIL"} ${offer.key.padEnd(28)} ` +
      `${offer.diverging ? "diverging " : "sequential"} own=${offer.own.padEnd(9)} ` +
      `${got.length}: ${got.join(" | ") || "(none)"}`,
  );
  if (!ok) problems.push(`${offer.key} was offered ${JSON.stringify(got)}`);
  // The folded row is the group's only visible line while the list is shut, so it has to name
  // the colourbar actually on screen. Nothing set an override in this loop, so that is the
  // Field's own.
  if (got.length > 0 && offer.folded !== OWN_LOOK[offer.own]) {
    problems.push(
      `${offer.key}: the folded row says ${JSON.stringify(offer.folded)}, ` +
        `drawn is ${OWN_LOOK[offer.own]}`,
    );
  }
}

// ---- 2 and 3. the water repaints, and the bar draws the same table ---------------------------
//
// On a fresh page, deliberately. The check above walks all fifteen Fields, which is fifteen full
// scene rebuilds under software rendering, and a screenshot after that stalled past 180 s -
// which is the shape `docs/BUGS.md` item 101 describes. Nothing these two claims measure depends
// on the state the first one leaves behind, so they get a page that has not been driven yet.
// This is separating independent claims, not editing a check until it passes.
await page.close();
page = await browser.newPage({ viewport: { width: 1400, height: 860 } });
page.on("pageerror", (e) => problems.push(`pageerror: ${e.message}`));
await page.goto(`${SERVER}/app.html`, { waitUntil: "load", timeout: 60000 });
await page.waitForFunction(() => !!window.__store?.getState().manifest, null, { timeout: 120000 });
await page.evaluate(() => document.querySelector("button.dive").click());
await page.waitForFunction(() => window.__store.getState().morph > 0.9, null, { timeout: 120000 });
await page.waitForTimeout(1200);

const frame = async () => decodePng(await page.screenshot({ timeout: 180000 }));
const differingShare = (a, b, box) => {
  let differing = 0;
  let total = 0;
  for (let y = box.y0; y < box.y1; y++) {
    for (let x = box.x0; x < box.x1; x++) {
      const i = (y * a.width + x) * 4;
      total++;
      const delta =
        Math.abs(a.data[i] - b.data[i]) +
        Math.abs(a.data[i + 1] - b.data[i + 1]) +
        Math.abs(a.data[i + 2] - b.data[i + 2]);
      if (delta > 24) differing++;
    }
  }
  return total === 0 ? 0 : (100 * differing) / total;
};

await page.evaluate(() => {
  const store = window.__store.getState();
  store.selectField("temperature");
  store.set("paletteOverride", null);
  store.set("openGroups", { ...store.openGroups, palette: true });
  store.set("paletteAlternates", true);
});
await page.waitForTimeout(1400);
const before = await frame();

await page.evaluate(() => window.__store.getState().set("paletteOverride", "gray"));
await page.waitForTimeout(1400);
const after = await frame();

// The band of glass between the two bays, below the bar and above the axis.
const water = { x0: 360, x1: 1040, y0: 120, y1: 620 };
const share = differingShare(before, after, water);
console.log(`\n  water repainted: ${share.toFixed(1)}% of the block band`);
if (share < 5) {
  problems.push(`switching the colourbar changed only ${share.toFixed(1)}% of the water`);
}

// Not a share of changed pixels, which only says the bar moved, and not a screenshot pixel
// either: the bar is 12 px tall over a dark panel and sampling its centre read the panel more
// often than the bar, so the check sat at a channel spread of 6 whatever the bar was drawing.
//
// The legend is a CSS `linear-gradient` built from the same table the water is drawn from, so
// read the stops out of `background-image` and hold them against that table directly. That is
// the claim - the water and the legend draw one palette - rather than a proxy for it.
const agreement = await page.evaluate(() => {
  const el = document.querySelector(".colourbar");
  const stops = [...getComputedStyle(el).backgroundImage.matchAll(/rgba?\(([^)]+)\)/g)].map((m) =>
    m[1].split(",").slice(0, 3).map((v) => Math.round(parseFloat(v))),
  );
  const store = window.__store.getState();
  return { stops, palette: store.activePalette(), own: store.field().palette };
});
const flat = agreement.stops.map((c) => Math.max(...c) - Math.min(...c));
const maxHue = Math.max(...flat);
console.log(
  `  legend is drawing ${agreement.stops.length} stops of "${agreement.palette}"` +
    ` while the Field's own is "${agreement.own}"`,
);
console.log(`  widest channel spread across those stops: ${maxHue} - a grey ramp has none`);
if (agreement.palette !== "gray") problems.push(`activePalette says ${agreement.palette}, not gray`);
if (maxHue > 12) {
  problems.push(`the legend is not drawing the chosen grey ramp: channel spread ${maxHue}`);
}

// ---- 4. the choice survives being sent ------------------------------------------------------
const link = await page.evaluate(() => window.__deeplink.currentViewUrl());
console.log(`  link: ${link.replace(/^https?:\/\/[^/]+/, "")}`);
if (!link.includes("palette=gray")) problems.push("the chosen colourbar is not in the copied link");

await page.goto(link, { waitUntil: "load", timeout: 120000 });
await page.waitForFunction(() => !!window.__store?.getState().manifest, null, { timeout: 120000 });
await page.waitForTimeout(2500);
const restored = await page.evaluate(() => window.__store.getState().paletteOverride);
console.log(`  restored from the link: ${restored}`);
if (restored !== "gray") problems.push(`the link restored ${restored}, not gray`);

// A link is the one input here a stranger writes, so a palette the Field may not be offered has
// to be refused rather than applied.
await page.goto(`${SERVER}/app.html?dive=1&field=temperature&palette=curl`, {
  waitUntil: "load",
  timeout: 120000,
});
await page.waitForFunction(() => !!window.__store?.getState().manifest, null, { timeout: 120000 });
await page.waitForTimeout(2500);
const refused = await page.evaluate(() => window.__store.getState().paletteOverride);
console.log(`  a diverging ramp asked for on a sequential Field: ${refused}`);
if (refused !== null) problems.push(`a link forced ${refused} onto a sequential Field`);

console.log(problems.length ? `\nPROBLEMS ${JSON.stringify(problems, null, 1)}` : "\nclean");
await browser.close();
process.exit(problems.length ? 1 : 0);
