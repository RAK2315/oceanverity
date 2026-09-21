import { useStore } from "../store";

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
 * they went.
 */
export function BayToggle({ side }: { side: "left" | "right" }) {
  const { panelsHidden, set } = useStore();
  const hidden = panelsHidden[side];
  const label = hidden
    ? `Show the ${side === "left" ? "controls" : "explanation"}`
    : `Hide the ${side === "left" ? "controls" : "explanation"}`;

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
