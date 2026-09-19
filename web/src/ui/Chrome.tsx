import { useCallback, useRef, useState } from "react";
import { copyCurrentView } from "../deeplink";
import { applyTheme, useStore } from "../store";

/**
 * Publish a band's measured height as a CSS custom property, so what sits beside it can clear it.
 *
 * Measured rather than written down because a band's height changes with the window and the type.
 * It was written for the source credits, whose wrapping made any fixed number wrong at the next
 * viewport; the credits band is gone (2026-09-11) and the top bar is what publishes now.
 */
function usePublishedHeight(name: string) {
  const watcher = useRef<ResizeObserver | null>(null);
  // A callback ref, not an effect. The element only exists once the manifest has loaded, so an
  // effect with no dependencies would re-create the observer on every render - and `Chrome`
  // re-renders on every store change, which during playback is every frame.
  return useCallback(
    (el: HTMLElement | null) => {
      watcher.current?.disconnect();
      if (!el) return;
      const publish = () => {
        document.documentElement.style.setProperty(
          name,
          `${Math.ceil(el.getBoundingClientRect().height)}px`,
        );
      };
      publish();
      watcher.current = new ResizeObserver(publish);
      watcher.current.observe(el);
    },
    [name],
  );
}

export function LoadingScreen() {
  return (
    <div className="loading">
      <div className="loading-mark" />
      <p>Reading INCOIS analysis and Argo profiles…</p>
    </div>
  );
}

/**
 * The two icons on the bar, drawn rather than typed.
 *
 * They were a sun, a moon, a chain link and a tick, all as characters. Measured, `☀` resolved
 * to Arial while everything around it was Chivo, and `🔗` is a colour emoji - so three controls
 * sitting on one 34 px baseline were rendered by three different font stacks at three weights,
 * one of them in full colour. A colour emoji is the loudest possible thing on a bar whose whole
 * job is to recede, and it is not a colour this design system has a role for.
 *
 * Drawn as 1.5 px strokes on a 24-unit grid, so they take the button's own `currentColor` and
 * change with the theme and the hover like every other mark in the frame.
 */
function ThemeIcon({ dark }: { dark: boolean }) {
  // The button offers the *other* theme, so the dark console shows a sun.
  return dark ? (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 3v2.2M12 18.8V21M4.6 4.6l1.6 1.6M17.8 17.8l1.6 1.6M3 12h2.2M18.8 12H21M4.6 19.4l1.6-1.6M17.8 6.2l1.6-1.6" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20.2 14.6A8.6 8.6 0 1 1 9.6 4a7 7 0 0 0 10.6 10.6z" />
    </svg>
  );
}

function CopyIcon({ state }: { state: "" | "copied" | "failed" }) {
  if (state === "copied") {
    return (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M5 12.6l4.6 4.6L19 7.8" />
      </svg>
    );
  }
  if (state === "failed") {
    return (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" aria-hidden="true">
        <path d="M12 6.5v7M12 17.2v.6" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
      <path d="M10.2 13.8a3.6 3.6 0 0 0 5.1 0l2.8-2.8a3.6 3.6 0 0 0-5.1-5.1L11.6 7.3" />
      <path d="M13.8 10.2a3.6 3.6 0 0 0-5.1 0l-2.8 2.8a3.6 3.6 0 0 0 5.1 5.1l1.4-1.4" />
    </svg>
  );
}

export function Chrome({ onDive }: { onDive: (into: boolean) => void }) {
  const store = useStore();
  const { manifest, stage, morph, field, timestepIndex, theme, touched, set } = store;
  // What the copy button last did, so it can say so for a moment. A control that fires and
  // shows nothing is a control a user presses three times.
  const [copied, setCopied] = useState<"" | "copied" | "failed">("");
  // Before the early return: a hook cannot be called conditionally. The top bar publishes its
  // measured height, so the bays under it can be exactly as tall as the gap.
  const bar = usePublishedHeight("--topbar-height");
  if (!manifest) return null;

  const flipTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    set("theme", next);
    applyTheme(next);
  };

  const spec = field();
  const stamp = manifest.timesteps[timestepIndex];
  // Split by kind: 5 to 14 of the instruments drawn at any step are anchored buoys, not Argo
  // floats, and calling them all floats is the same class of error as counting every instrument
  // in the bake as "reporting" when only the ones near this date are.
  const reporting = store.reportingByKind();
  const inVolume = morph > 0.5;

  return (
    <>
      <header className="topbar" ref={bar}>
        {/*
          * The masthead, on one baseline.
          *
          * It was a two-line lockup - a tracked mono wordmark in dim ink over its own metadata
          * in dimmer ink - which is the shape a product header takes when nobody has decided
          * what the header is for. Two greys stacked read as a logo someone dropped in. The
          * wordmark keeps its letterspaced caps, which `DESIGN.md` reserves for exactly this one
          * place, and takes full ink; the provenance sits beside it past a rule, at the weight
          * of a caption, because that is what it is.
          */}
        <div className="brand">
          <span className="brand-mark">SAMUDRA<span className="brand-dim">·3D</span></span>
          <span className="brand-sub">INCOIS</span>
        </div>

        {/*
          * What you are looking at, as the largest thing on the bar.
          *
          * The hierarchy used to run the other way: "Dive into the water" was the loudest object
          * up here and the Field and the date were two small mono readouts pushed against it, in
          * a row of buttons. For the reader this console is built for that is backwards. A
          * forecaster presses dive once and then checks *which field, which analysis* constantly
          * - it is the state they are holding in their head, and the one thing that being wrong
          * about invalidates everything they conclude. So the state gets the bar's biggest type
          * and the position the eye reaches first, and the actions get the end and a quieter
          * weight. It sits after the masthead rather than on the bar's centre; the note on
          * `.topbar-state` in `styles.css` has the measurements that settled that.
          */}
        <div className="topbar-state">
          {/* The full name in the tooltip, so the ellipsis at the 980 px floor loses nothing. */}
          <span className="state-field" title={spec?.label ?? undefined}>
            {spec?.label.replace("Sea Water ", "") ?? "-"}
          </span>
          <span className="state-on">on</span>
          <span className="state-date">
            {stamp ? new Date(stamp).toISOString().slice(0, 10) : "-"}
          </span>
        </div>

        {/*
          * Five controls in one flat row of equal height and equal gap is five peers, and a
          * reader has to price all five before pressing anything. They are not peers: two are
          * settings on this browser, two are doors into the same platform, and one is the thing
          * the whole screen is for. So the row is three groups now, set apart by their spacing
          * and one rule - the settings keep their 34 px circles and are pushed to the far left
          * of the cluster, the two doors sit together as a pair, and the dive button keeps the
          * end and the only fill on the bar.
          */}
        <div className="topbar-right">
          <div className="topbar-utilities">
            <button
              className="icon-button"
              onClick={flipTheme}
              title={theme === "dark" ? "Switch to light console" : "Switch to dark console"}
              aria-label={theme === "dark" ? "Switch to light console" : "Switch to dark console"}
            >
              <ThemeIcon dark={theme === "dark"} />
            </button>
            {/*
              * The link to what is on screen.
              *
              * `applyDeepLink` has read these parameters since the requirements page was built
              * and nothing could write one. That gap is the whole "e-learning initiatives"
              * clause: a teacher's worksheet is six links, and a forecaster hands a colleague a
              * view rather than a description of one. See `deeplink.ts`.
              */}
            <button
              className={`icon-button${copied === "copied" ? " done" : ""}`}
              onClick={async () => {
                const result = await copyCurrentView();
                setCopied(result.copied ? "copied" : "failed");
                window.setTimeout(() => setCopied(""), 2400);
              }}
              title="Copy a link to exactly this view"
              aria-label="Copy a link to exactly this view"
            >
              <CopyIcon state={copied} />
            </button>
          </div>

          <div className="topbar-doors">
            {/* Offered on the top bar rather than buried, because the people it is for are the
                ones who would never find it in a panel. */}
            <button
              className="ghost tour-start"
              onClick={() => set("tourStep", 0)}
              title="A guided walk through every control, in six chapters"
            >
              Show me around
            </button>
            {/*
              * The second door. PS 26067 names school students, the public and policymakers,
              * and nineteen variables in six groups is the wrong first minute for all three.
              * One button, and everything outreach lives behind it rather than in this bar.
              */}
            <button
              className="ghost"
              onClick={() => set("explore", true)}
              title="The same platform, as a list of questions"
            >
              Explore
            </button>
          </div>

          <button
            className={`dive ${inVolume ? "dive-up" : ""}`}
            onClick={() => onDive(!inVolume)}
            disabled={stage === "diving"}
          >
            {stage === "diving" ? "…" : inVolume ? "Return to globe" : "Dive into the water"}
          </button>
        </div>
      </header>

      {!inVolume && stage !== "diving" && !touched && (
        <div className="cue">
          <p className="cue-title">India&apos;s Exclusive Economic Zone</p>
          {/* Not manifest.floatCount. That is every Float in the bake; this card is a claim
              about what is on the water right now, and a Float whose nearest cast is outside
              the window is not drawn. At the step the app opens on the two differ by 37. */}
          <p className="cue-body">
            {reporting.floats} Argo floats
            {reporting.moorings > 0 && ` and ${reporting.moorings} moored buoys`} reporting over
            the Arabian Sea, the Bay of Bengal and the equatorial Indian Ocean on{" "}
            {stamp ? stamp.slice(0, 10) : "this date"}. The colour on the sea is INCOIS&apos;s
            own gridded analysis - the same field you are about to fly into.
          </p>
        </div>
      )}

      {/*
        * No credits band. It was a folded "Sources" line under the time axis, and the owner removed
        * it on 2026-09-11, knowing the attribution for Argo, INCOIS, Copernicus and NOAA is a
        * licence obligation. The console now credits no source itself; every full attribution
        * string is on `provenance.html`, which the landing page links to. If a console link to it
        * is ever wanted, that is where the credit should point.
        */}
    </>
  );
}
