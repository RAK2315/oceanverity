import { useEffect, useMemo } from "react";
import { buildCaseSteps, buildFishingSteps } from "../cases";
import type { ExploreHelpers } from "../explore";
import { useStore } from "../store";
import { PausedCard } from "./Tour";

/**
 * The storm walkthrough's card. Same place, shape and rules as the tour's: it drives the scene
 * through the store, touching any control pauses it, and the caveat sits on the card beside the
 * step rather than behind a link. The source line names IMD, because the track is theirs.
 */
export function CaseCard({ helpers, onDive }: { helpers: ExploreHelpers; onDive: (into: boolean) => void }) {
  const stormCase = useStore((s) => s.stormCase);
  const caseStep = useStore((s) => s.caseStep);
  const cardPaused = useStore((s) => s.cardPaused);
  const walkthrough = useStore((s) => s.walkthrough);
  const manifest = useStore((s) => s.manifest);
  const steps = useMemo(() => {
    if (walkthrough === "fishing") return manifest ? buildFishingSteps(manifest, onDive) : [];
    return stormCase ? buildCaseSteps(stormCase, onDive) : [];
  }, [walkthrough, manifest, stormCase, onDive]);
  // The storm card names the storm; the fishing card names what it walks through.
  const name = walkthrough === "fishing" ? "Under a fishing advisory" : `Cyclone ${stormCase?.name ?? ""}`;
  const step = caseStep === null ? undefined : steps[caseStep];

  // Applied when a step opens and when a paused step is continued, never while paused.
  useEffect(() => {
    if (caseStep === null || !step || cardPaused) return;
    step.enter(helpers);
    // A step selects a Field, which is a store action that may pause walkthroughs; the index is
    // put back and the pause cleared so the card stays open on the step it just applied.
    const now = useStore.getState();
    if (now.caseStep !== caseStep || now.cardPaused) useStore.setState({ caseStep, cardPaused: false });
    // `helpers` closes over the scene and is rebuilt on renders; the step index is what matters.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseStep, step, cardPaused]);

  if (caseStep === null || !step) return null;
  const last = caseStep === steps.length - 1;
  const end = () => useStore.setState({ caseStep: null, cardPaused: false });

  if (cardPaused) {
    return <PausedCard label={name} title={step.title} onEnd={end} />;
  }

  return (
    <aside className="tour case" role="dialog" aria-label={`${name} walkthrough`}>
      <div className="tour-head">
        <span className="tour-count">
          {name} &middot; {caseStep + 1} of {steps.length}
        </span>
        <button className="ghost" onClick={end} aria-label="End the walkthrough">
          ✕
        </button>
      </div>
      <h2 className="tour-title">{step.title}</h2>
      <p className="tour-body">{step.body}</p>
      {step.caution && <p className="case-note">{step.caution}</p>}
      <div className="tour-progress" aria-hidden="true">
        <span style={{ transform: `scaleX(${(caseStep + 1) / steps.length})` }} />
      </div>
      <div className="tour-actions">
        <button
          className="ghost"
          onClick={() => useStore.setState({ caseStep: Math.max(0, caseStep - 1) })}
          disabled={caseStep === 0}
        >
          Back
        </button>
        <button
          className="primary"
          onClick={() => useStore.setState({ caseStep: last ? null : caseStep + 1 })}
        >
          {last ? "Explore on your own" : "Next"}
        </button>
      </div>
    </aside>
  );
}
