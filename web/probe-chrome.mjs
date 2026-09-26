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
  ".mode-switch",
  ".field-tabs button",
  ".palette-current",
  ".palette-list button:not(.on)",
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
  // ---- a bay tab exists only where there is a bay --------------------------------------------
  //
  // On the globe, nothing is mounted in the right bay until the reader touches a control, so the
  // right tab docked to an edge that was not there: measured at 1400x800, a 22x34 square at
  // 1030,61 beside a cue card at 1062,88. It reads as that card's close button, and pressing it
  // does hide the card, because the fold rule covers `.cue` too. Reported by the owner,
  // `docs/BUGS.md` item 139. Checked before the dive, which is the only state it happens in.
  const bays = await page.evaluate(() => ({
    left: !!document.querySelector(".bay-left"),
    right: !!document.querySelector(".bay-right"),
    leftPanel: !!document.querySelector("aside.panel-left"),
    rightPanel: !!document.querySelector(".panel-right, .panel-section"),
  }));
  console.log(`  globe view, bays: ${JSON.stringify(bays)}`);
  if (bays.right !== bays.rightPanel || bays.left !== bays.leftPanel) {
    problems.push(`${theme}: a bay tab is drawn beside a bay that holds nothing: ${JSON.stringify(bays)}`);
  }

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
    // The alternates fold, so their text is not in the DOM until it is unfolded.
    store.set("paletteAlternates", true);
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

  // ---- the map key names the colour that is actually drawn -----------------------------------
  //
  // Six colours are written twice: in `SCENE_COLOURS`, which is what the WebGL geometry uses,
  // and in `styles.css`, which is the swatch in the map key beside the word for it. Nothing
  // compared them, and a legend that names a colour not on screen is the same failure class as
  // a colourbar that does not bend with its water - the pair that got the log scale cut once
  // for having two copies of one curve. A synthetic element is used rather than the real
  // swatch, so the check holds whether or not the reader has the map key open.
  const swatches = await page.evaluate(() => {
    const scene = window.__scene.themeColoursForTest();
    const pairs = [
      ["swatch float", "float", "background"],
      ["swatch track", "track", "background"],
      ["swatch coast", "coast", "background"],
      ["swatch drift", "drift", "background"],
      ["swatch section", "section", "background"],
      ["swatch storm", "storm", "background"],
      ["swatch float hollow", "biasOutline", "background"],
    ];
    const hex = (rgb) => {
      const parts = rgb.match(/[\d.]+/g)?.slice(0, 3).map(Number) ?? [];
      if (parts.length < 3) return rgb;
      return "#" + parts.map((n) => Math.round(n).toString(16).padStart(2, "0")).join("");
    };
    const host = document.createElement("div");
    host.style.position = "fixed";
    host.style.left = "-9999px";
    document.body.appendChild(host);
    const out = pairs.map(([className, key]) => {
      const span = document.createElement("span");
      span.className = className;
      host.appendChild(span);
      const drawn = hex(getComputedStyle(span).backgroundColor);
      return { className, key, css: drawn, scene: scene[key] ?? null };
    });
    host.remove();
    return out;
  });
  for (const row of swatches) {
    const agree = row.scene !== null && row.css.toLowerCase() === row.scene.toLowerCase();
    console.log(`  ${agree ? "ok  " : "FAIL"} .${row.className.replace(/ /g, ".")}  key ${row.css} / scene ${row.scene}`);
    if (!agree) {
      problems.push(
        `${theme}: the map key draws .${row.className.replace(/ /g, ".")} as ${row.css} and the ` +
          `scene draws ${row.key} as ${row.scene}: the legend names a colour not on screen`,
      );
    }
  }

  // ---- the depth ruler's caption stays where it is when the map key is dragged ---------------
  //
  // The caption reads the map key's box every frame to find a floor it must stay above, which is
  // right for the time axis and wrong for a legend the reader can drag anywhere: measured at
  // 1400x800, moving the key from y 570 to y 214 moved the caption from y 547 to y 215, and
  // parking it in the top right corner - clear of the caption's column, with nothing to avoid -
  // still pulled the caption up to y 30. Reported by the owner, `docs/BUGS.md` item 142. It is a
  // band only where it overlaps the caption's column and reaches down to it.
  //
  // Both toggles are put back first, because the caption is placed against the left panel's
  // width and the right bay is folded nowhere in this run - but a check that depends on a state
  // an earlier block set is a check that moves when that block does.
  const rulerBefore = await page.evaluate(() => {
    const note = document.querySelector(".ruler-note")?.getBoundingClientRect();
    return note ? { x: Math.round(note.left), y: Math.round(note.top) } : null;
  });
  const key = await page.$(".mapkey");
  const keyBox = key ? await key.boundingBox() : null;
  if (!rulerBefore || !keyBox) {
    problems.push(`${theme}: no depth ruler caption or no map key to drag against it`);
  } else {
    for (const [tag, toX, toY] of [
      ["top right", 1000, 150],
      ["over the column, high", 300, 260],
    ]) {
      const from = await (await page.$(".mapkey")).boundingBox();
      await page.mouse.move(from.x + 140, from.y + from.height - 10);
      await page.mouse.down();
      await page.mouse.move(toX, toY, { steps: 12 });
      await page.mouse.up();
      await page.waitForTimeout(700);
      const after = await page.evaluate(() => {
        const note = document.querySelector(".ruler-note")?.getBoundingClientRect();
        const k = document.querySelector(".mapkey")?.getBoundingClientRect();
        return {
          note: note ? { x: Math.round(note.left), y: Math.round(note.top) } : null,
          moved: k ? Math.round(k.top) : null,
        };
      });
      console.log(
        `  map key dragged ${tag} to y ${after.moved}: caption ${JSON.stringify(after.note)} ` +
          `(was ${JSON.stringify(rulerBefore)})`,
      );
      if (!after.note || after.note.y !== rulerBefore.y || after.note.x !== rulerBefore.x) {
        problems.push(
          `${theme}: dragging the map key ${tag} moved the depth ruler's caption from ` +
            `${JSON.stringify(rulerBefore)} to ${JSON.stringify(after.note)}`,
        );
      }
    }
  }

  await context.close();
}

console.log(problems.length ? `\nPROBLEMS ${JSON.stringify(problems, null, 1)}` : "\nclean");
await browser.close();
process.exit(problems.length ? 1 : 0);
