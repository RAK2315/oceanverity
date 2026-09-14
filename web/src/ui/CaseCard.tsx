import { useEffect, useMemo } from "react";
import { buildCaseSteps } from "../cases";
import type { ExploreHelpers } from "../explore";
import { useStore } from "../store";

/**
 * The storm walkthrough's card. Same place, shape and rules as the tour's: it drives the scene
 * through the store, touching any control ends it, and the caveat sits on the card beside the
 * step rather than behind a link. The source line names IMD, because the track is theirs.
 */
export function CaseCard({ helpers, onDive }: { helpers: ExploreHelpers; onDive: (into: boolean) => void }) {
  const stormCase = useStore((s) => s.stormCase);
  const caseStep = useStore((s) => s.caseStep);
  const steps = useMemo(() => (stormCase ? buildCaseSteps(stormCase, onDive) : []), [stormCase, onDive]);
  const step = caseStep === null ? undefined : steps[caseStep];

  useEffect(() => {
    if (caseStep === null || !step) return;
    step.enter(helpers);
    // A step selects a Field, which is a store action that may clear other walkthroughs; the
    // index is put back so the card stays open on the step it just applied.
    if (useStore.getState().caseStep !== caseStep) useStore.setState({ caseStep });
    // `helpers` closes over the scene and is rebuilt on renders; the step index is what matters.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseStep, step]);

  if (!stormCase || caseStep === null || !step) return null;
  const last = caseStep === steps.length - 1;

  return (
    <aside className="tour case" role="dialog" aria-label={`Cyclone ${stormCase.name} walkthrough`}>
      <div className="tour-head">
        <span className="tour-count">
          Cyclone {stormCase.name} &middot; {caseStep + 1} of {steps.length}
        </span>
        <button className="ghost" onClick={() => useStore.setState({ caseStep: null })} aria-label="End the walkthrough">
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
