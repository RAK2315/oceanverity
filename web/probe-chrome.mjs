/**
 * Every text role in the console chrome, against the ground actually behind it, in both themes.
 *
 * `probe-landing.mjs` measures the hero this way and nothing measured the console, which is the
 * larger surface and the one a forecaster reads all day. Two roles were failing WCAG AA when this
 * was first run by hand: the unlabelled timeline ticks at **2.55:1** on dark and 2.47 on light -
 * `--outline` is a hairline colour and those are buttons a user clicks - and the `baked` stamp at
 * **3.05:1** on light, from an `opacity: 0.72` sitting on top of a role that already passes.
 *
 * Two traps, both of which this check fell into before it asserted anything, and both of which
 * make a real failure read as a pass or a healthy role read as catastrophic:
 *
 *   1. **Fold in `opacity`.** The element's own and every ancestor's, multiplied into the ink's
 *      alpha. Leaving it out is exactly how `.generated` at 0.72 of the tertiary role reported
 *      5.17:1 when it was 3.05.
 *   2. **Do not measure mid-fade.** The panels enter on a `fade-up`, so a role read while its
 *      panel is still arriving measures against alpha 0 and comes back as 1:1. Reduced motion on
 *      the context, and a wait on the panel being opaque and on `getAnimations()` settling.
 *
 *   node probe-chrome.mjs        (needs a preview server on 4173)
 */
import { chromium } from "playwright";

const SERVER = process.env.PREVIEW_URL ?? "http://localhost:4173";

// Every role in the four bands of the frame, plus the two panels' own text. Named rather than
// discovered, because a role that stops being rendered should fail this as loudly as one that
// goes unreadable - a missing selector is reported, never skipped.
const ROLES = [
  ".brand-mark",
  ".brand-sub",
  ".state-field",
  ".state-on",
  ".state-date",
  ".tour-start",
  ".topbar-doors .ghost:not(.tour-start)",
  ".dive",
  ".icon-button",
  ".timeline-step",
  ".timeline-step b",
  ".timeline-note",
  ".timeline-ticks button.bare",
  ".timeline-ticks button:not(.bare):not(.on)",
  ".attribution-label",
  ".attribution-lead",
  ".attribution-more",
  ".generated",
  ".mode-switch",
  ".field-tabs button",
  ".profile-facts",
  ".pill",
  ".why > summary",
  ".analysis-note",
];

const problems = [];
const browser = await chromium.launch({
  args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});

for (const theme of ["dark", "light"]) {
  const context = await browser.newContext({
    viewport: { width: 1366, height: 768 },
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  page.on("pageerror", (e) => problems.push(`pageerror: ${e.message}`));

  await page.goto(`${SERVER}/app.html`, { waitUntil: "load", timeout: 60000 });
  await page.waitForFunction(() => !!window.__store?.getState().manifest, null, { timeout: 120000 });
  // Both halves of the theme, because the scene is part of it: `data-theme` paints the chrome and
  // the store paints the WebGL. One alone gives a mismatched frame that looks like an app bug.
  await page.evaluate((t) => {
    document.documentElement.dataset.theme = t;
    window.__store.getState().set("theme", t);
  }, theme);
  await page.evaluate(() => document.querySelector("button.dive").click());
  await page.waitForFunction(() => window.__store.getState().morph > 0.9, null, { timeout: 120000 });
  await page
    .waitForFunction(() => window.__store.getState().collocationsReady, null, { timeout: 120000 })
    .catch(() => {});

  // Open the panels whose roles are on the list: a comparison for the profile roles, and the
  // Colourbar group, whose buttons are not in the DOM while it is shut.
  await page.evaluate(() => {
    const store = window.__store.getState();
    store.set("selectedFloatId", store.floats[0].id);
    store.set("touched", "");
    store.set("openGroups", { ...store.openGroups, palette: true, field: true });
  });
  await page.waitForTimeout(1500);
  await page
    .waitForFunction(
      () => {
        const el = document.querySelector(".profile-facts");
        return el && parseFloat(getComputedStyle(el.closest(".panel-right") ?? el).opacity) > 0.99;
      },
      null,
      { timeout: 60000 },
    )
    .catch(() => {});
  await page
    .waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"), null, {
      timeout: 20000,
    })
    .catch(() => {});
  await page.waitForTimeout(500);

  const rows = await page.evaluate((selectors) => {
    const parse = (colour) => {
      const parts = (colour.match(/[\d.]+/g) ?? [0, 0, 0, 1]).map(Number);
      return parts.length > 3 ? parts : [...parts, 1];
    };
    const over = (fg, bg) => fg.slice(0, 3).map((v, i) => v * fg[3] + bg[i] * (1 - fg[3]));
    const lum = (rgb) => {
      const s = rgb.map((v) => {
        const c = v / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2];
    };
    const ratio = (a, b) => {
      const [hi, lo] = [lum(a), lum(b)].sort((p, q) => q - p);
      return (hi + 0.05) / (lo + 0.05);
    };
    // The ground actually behind it: every translucent background up the tree, composited down
    // onto the page. A single `backgroundColor` lookup finds `rgba(0,0,0,0)` and lies.
    const groundOf = (el) => {
      const stack = [];
      for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
        const bg = parse(getComputedStyle(n).backgroundColor);
        if (bg[3] > 0) stack.push(bg);
      }
      stack.push([255, 255, 255, 1]);
      let ground = stack.pop();
      while (stack.length) ground = [...over(stack.pop(), ground), 1];
      return ground;
    };

    return selectors.map((selector) => {
      const el = document.querySelector(selector);
      if (!el) return { selector, missing: true };
      const style = getComputedStyle(el);
      const fg = parse(style.color);
      let alpha = 1;
      for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
        alpha *= parseFloat(getComputedStyle(n).opacity);
      }
      fg[3] *= alpha;
      const ground = groundOf(el);
      const px = parseFloat(style.fontSize);
      const large = px >= 18 || (px >= 14 && Number(style.fontWeight) >= 700);
      return {
        selector,
        px,
        weight: style.fontWeight,
        alpha: Number(alpha.toFixed(2)),
        ratio: Number(ratio(over(fg, ground), ground.slice(0, 3)).toFixed(2)),
        need: large ? 3 : 4.5,
      };
    });
  }, ROLES);

  console.log(`\n=== ${theme} ===`);
  for (const row of rows) {
    if (row.missing) {
      console.log(`  MISSING ${row.selector}`);
      problems.push(`${theme}: ${row.selector} is not on screen to measure`);
      continue;
    }
    const pass = row.ratio >= row.need;
    if (!pass) {
      problems.push(
        `${theme}: ${row.selector} is ${row.ratio}:1 at ${row.px}px, needs ${row.need}`,
      );
    }
    console.log(
      `  ${pass ? "ok  " : "FAIL"} ${String(row.ratio).padStart(6)} (needs ${row.need})  ` +
        `${row.px}px/${row.weight} a=${row.alpha}  ${row.selector}`,
    );
  }
  await context.close();
}

console.log(problems.length ? `\nPROBLEMS ${JSON.stringify(problems, null, 1)}` : "\nclean");
await browser.close();
process.exit(problems.length ? 1 : 0);
