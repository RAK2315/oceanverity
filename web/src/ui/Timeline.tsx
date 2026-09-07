import { useCallback, useRef } from "react";
import { useStore } from "../store";

/**
 * Publish the axis band's measured height, so the bays above it end exactly where it starts.
 *
 * The frame is four bands - the bar, two bays and the foot - and each one measures itself rather
 * than every other one guessing. The axis wraps its ticks differently at different widths, so a
 * number written down here would be wrong at the next viewport.
 */
function usePublishedHeight(name: string) {
  const watcher = useRef<ResizeObserver | null>(null);
  return useCallback(
    (el: HTMLElement | null) => {
      watcher.current?.disconnect();
      if (!el) return;
      const publish = () =>
        document.documentElement.style.setProperty(
          name,
          `${Math.ceil(el.getBoundingClientRect().height)}px`,
        );
      publish();
      watcher.current = new ResizeObserver(publish);
      watcher.current.observe(el);
    },
    [name],
  );
}

export function Timeline() {
  const { manifest, timestepIndex, playing, biasMode, set } = useStore();
  const band = usePublishedHeight("--timeline-height");
  if (!manifest) return null;

  const steps = manifest.timesteps;
  const current = steps[timestepIndex];
  const shown = current ? new Date(current).toISOString().slice(0, 10) : "-";

  return (
    <div className="timeline" ref={band}>
      <button
        className="play"
        onClick={() => {
          set("touched", "timestep");
          set("playing", !playing);
        }}
        // The label used to say "Play" in both states, so a screen reader announced the
        // stop control as a start control.
        aria-label={playing ? "Pause the time animation" : "Play the time animation"}
        aria-pressed={playing}
      >
        {playing ? "❚❚" : "▶"}
      </button>

      <div className="timeline-track">
        <input
          type="range"
          min={0}
          max={steps.length - 1}
          step={1}
          value={timestepIndex}
          aria-label="Analysis date"
          aria-valuetext={shown}
          onFocus={() => set("touched", "timestep")}
          onChange={(e) => {
            set("touched", "timestep");
            set("timestepIndex", Number(e.target.value));
          }}
        />
        {/*
          * Buttons, not spans. These were clickable and unreachable by keyboard, which made the
          * tick strip a mouse-only duplicate of a control the slider already offers.
          *
          * Every step stays clickable, but only every other one carries its date. Twelve
          * five-character labels need more width than the track has on a 1366 px screen, and
          * they ran into each other - "04-1004-2004-30" - which reads as a broken axis. The
          * unlabelled steps keep their accessible name, so nothing is lost to a screen reader.
          */}
        <div className="timeline-ticks">
          {steps.map((stamp, index) => {
            const date = new Date(stamp).toISOString().slice(0, 10);
            const labelled = index % 2 === 0 || index === steps.length - 1;
            return (
              <button
                type="button"
                key={stamp}
                className={`${index === timestepIndex ? "on" : ""}${labelled ? "" : " bare"}`}
                aria-label={`Show the analysis of ${date}`}
                aria-current={index === timestepIndex}
                onClick={() => {
                  set("touched", "timestep");
                  set("timestepIndex", index);
                }}
              >
                {labelled ? date.slice(5) : "·"}
              </button>
            );
          })}
        </div>
      </div>

      {/*
        * What the axis knows that nothing else on screen does: which of twelve, and what a step
        * is worth.
        *
        * It used to print the date, which is the **third** copy of that date on the glass - the
        * top bar carries it at 14 px in the centre of the screen, and the tick under the handle
        * is highlighted with it. `DESIGN.md` says a figure that is already a readout somewhere
        * else belongs in one place; the position in the run was the figure nothing was carrying.
        */}
      <div className="timeline-stamp">
        <span className="timeline-step">
          Step <b>{timestepIndex + 1}</b> of <b>{steps.length}</b>
        </span>
        {/*
          * The bias map does not move with the timeline, and the only place that was said was
          * inside the map key - which folds, and is remembered folded.
          *
          * Each marker is drawn where its own comparison was taken, across all twelve analyses,
          * because a residual measured at one position on one date would be a number on the
          * wrong water anywhere else. That is right and it is documented. What it looked like
          * was pressing play, watching the field animate, and watching every instrument stand
          * still - which reads as a broken animation. So the axis says it, on the band whose
          * button was just pressed, whenever the mode is on.
          */}
        {biasMode ? (
          <span className="timeline-note pinned">Instruments pinned to their own cast dates</span>
        ) : (
          <span className="timeline-note">10-day analysis</span>
        )}
      </div>
    </div>
  );
}
