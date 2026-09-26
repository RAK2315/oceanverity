import { useLayoutEffect, useState } from "react";
import { useStore } from "../store";

/** What each bay holds. Presence in the DOM, not width; see `useBayFilled`. */
const BAY_PANELS = {
  left: "aside.panel-left",
  right: ".panel-right, .panel-section",
} as const;

/**
 * Whether that bay holds a panel at all.
 *
 * Nothing is mounted in the right bay on the globe until the reader touches a control. The cue
 * card sits in that column but is not a panel, so the tab docked to an edge that was not there:
 * measured at 1400x800, the card's box was 320x149 at 1062,88 and the tab was at 1030,61, a
 * detached square 32 px off the card's left edge and 27 px above its top. It reads as that
 * card's close button, and pressing it does in fact hide the card - the fold rule covers `.cue`
 * as well - which is the reading confirmed rather than corrected. A tab that folds a bay the
 * reader cannot see is not a control.
 *
 * **Presence, not width.** A folded panel is `display: none` and measures zero, and that is
 * exactly the state the tab has to survive in order to bring the panel back. The standing
 * `getBoundingClientRect()` rule - zero is a number - is here read the other way round: what is
 * asked is whether the panel is mounted, which `querySelector` answers and a rect cannot.
 *
 * No observer. Every condition that mounts one of those panels is store state, and this
 * component subscribes to the whole store, so re-reading after each render keeps it in step.
 */
function useBayFilled(side: "left" | "right"): boolean {
  const [filled, setFilled] = useState(false);
  useLayoutEffect(() => {
    const now = !!document.querySelector(BAY_PANELS[side]);
    setFilled((was) => (was === now ? was : now));
  });
  return filled;
}

/**
 * The button that folds one bay away, and the tab that brings it back.
 *
 * The water is the product and the two bays take 663 px of a 1366 px screen between them. A
 * reader who has set the controls the way they want them wants the block, and a presenter
 * showing it to a room wants it more - which is exactly the itch that made `capture.mjs` reach
 * for kiosk mode to get a clean frame and come back with the Explore loop running in it.
 *
 * So this is a CSS state and nothing else. It mounts no component, starts no timer and changes
 * nothing the scene reads. Escape is not bound to it either: Escape already closes a comparison
 * and leaves kiosk, and a third meaning would make it the key nobody trusts.
 *
 * The control does not disappear with the panel it folds. It docks to the frame's inner edge as
 * a small tab, because a control whose only affordance for coming back is the same control that
 * hid it has to still be on screen - the alternative is a reader with no panels and no idea how
 * they went. It does disappear when its bay holds nothing at all, which is a different
 * question and a different state: see `useBayFilled`.
 */
export function BayToggle({ side }: { side: "left" | "right" }) {
  const { panelsHidden, set } = useStore();
  const filled = useBayFilled(side);
  const hidden = panelsHidden[side];
  const label = hidden
    ? `Show the ${side === "left" ? "controls" : "explanation"}`
    : `Hide the ${side === "left" ? "controls" : "explanation"}`;

  if (!filled) return null;

  return (
    <button
      type="button"
      className={`bay-toggle bay-${side}${hidden ? " folded" : ""}`}
      aria-expanded={!hidden}
      title={label}
      aria-label={label}
      onClick={() => set("panelsHidden", { ...panelsHidden, [side]: !hidden })}
    >
      {/*
        * One chevron, rotated by the state rather than swapped for its mirror.
        *
        * Two SVGs would be two things to keep in step, and this is the same mark pointing the
        * way the panel will travel: outward to fold, inward to come back.
        */}
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M14.5 5.5L8 12l6.5 6.5" />
      </svg>
    </button>
  );
}
