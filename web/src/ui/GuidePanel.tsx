import { useState } from "react";
import {
  GUIDE,
  describeIsosurface,
  describePalette,
  describeView,
  fillFigures,
  guideFigures,
} from "../guide";
import { axisToDepth } from "../scene/geography";
import { UPLOAD_GROUP, useStore } from "../store";
import { isDiverging } from "../transfer";

/** Remembered per browser, like the map key's fold, so a reader who shut it once is not asked again. */
const VIEW_OPEN_KEY = "samudra.guide.view";

/**
 * The "what am I looking at" panel.
 *
 * Every control on the left is meaningless without this. A slider labelled "Feature emphasis"
 * tells a forecaster nothing; knowing that it makes still water transparent so the thermocline
 * shows through tells them everything, and turns a toy into an instrument.
 *
 * When a control is touched it explains that control. Otherwise it describes the current view.
 * The Collocation panel takes this space when a Float is selected, because at that point the
 * comparison *is* the answer to "what am I looking at".
 */
export function GuidePanel() {
  const store = useStore();

  // The "What you are looking at" description folds. It is a paragraph sitting over the right
  // side of the water, it says the same thing every time the view is the same, and a reader who
  // has read it once wants the water back - the argument the map key's fold already made, so it
  // is the same disclosure, remembered the same way. Only the description folds: an explanation
  // of a control the reader just touched is the answer to a question they asked, and it keeps
  // its close button. Before the early returns, because a hook cannot be called conditionally.
  const [viewOpen, setViewOpen] = useState(() => {
    try {
      return window.localStorage.getItem(VIEW_OPEN_KEY) !== "closed";
    } catch {
      return true; // storage refused is not a reason to hide the description
    }
  });
  const toggleView = () => {
    setViewOpen((was) => {
      try {
        window.localStorage.setItem(VIEW_OPEN_KEY, was ? "closed" : "open");
      } catch {
        // Failing to remember must never cost the control.
      }
      return !was;
    });
  };

  const { manifest, touched, selectedFloatId, selectedAnomaly, morph, set } = store;
  const spec = store.field();

  // An explanation used to time out after fourteen seconds, which meant a reader who paused to
  // look at the water lost the answer to the question they had just asked. It now stays until
  // they touch another control or close it, which is what the close button is for.

  // On the globe the panel stays out of the way until the user touches something, because the
  // cue card is already explaining the view there. The moment a control is touched it takes
  // over - otherwise changing the palette or the surface level from the globe explains nothing.
  // The Collocation and the Anomaly Feature panels both take this space, because at the moment
  // one is open it *is* the answer to "what am I looking at".
  // The right-hand panel answers whichever question was asked last.
  //
  // This used to return null whenever a Float was selected, full stop - so touching any control
  // while a comparison was open produced no explanation at all, silently. Worst on the bias
  // map, where clicking a row *is* selecting a float: the entry explaining the control could
  // only be read by opening the group and then not using it. Selecting an instrument clears
  // `touched`, so the comparison still wins the moment it is opened, and the guide's close
  // button puts it back.
  if (!manifest || !spec || selectedAnomaly !== null) return null;
  if (selectedFloatId && !touched) return null;
  if (morph < 0.5 && !touched) return null;

  // The colourbar entry is built rather than written, because it names the palette the current
  // Field carries. Every other entry is a fixed piece of prose.
  // Every measured figure an entry quotes comes from the bake, not from the entry. See
  // `guideFigures`: a token with nothing behind it takes its bullet out rather than printing
  // a number from a bake that is no longer on disk.
  const written =
    touched === "palette"
      ? describePalette(store.activePalette(), spec.label, spec.group === UPLOAD_GROUP)
      : touched === "isosurface"
        ? describeIsosurface(spec.key, spec.units)
        : touched
          ? GUIDE[touched]
          : undefined;
  const entry = written
    ? fillFigures(written, guideFigures({ manifest, anomalies: store.anomalies }))
    : undefined;
  const volume = manifest.volume;

  return (
    <aside className={`panel panel-right guide${!entry && !viewOpen ? " view-shut" : ""}`}>
      {entry ? (
        <>
          <div className="guide-head">
            <span className={`guide-kind ${entry.kind}`}>{KIND_LABEL[entry.kind]}</span>
            <button className="ghost" onClick={() => set("touched", null)} aria-label="Close">
              ✕
            </button>
          </div>
          <h2 className="guide-title">{entry.title}</h2>

          {/*
            * One sentence, then two short lists.
            *
            * This was three <dd> blocks of prose, 40 to 70 words each, under the headings "What
            * it changes", "What that means" and "What to look for" - about 170 words a control,
            * which nobody reads while a demo is running. The definition keeps its sentence and
            * loses its heading, because a heading over one line is noise; the other two became
            * bullets under headings short enough to scan past.
            */}
          <p className="guide-does">{entry.does}</p>

          <h3 className="guide-label">Why it matters</h3>
          <ul className="guide-points">
            {entry.means.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>

          <h3 className="guide-label">Look for</h3>
          <ul className="guide-points">
            {entry.look.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>

          {entry.tryThis && <p className="guide-try">{entry.tryThis}</p>}
        </>
      ) : (
        <>
          <div className="guide-head">
            <button
              type="button"
              className="guide-view-toggle"
              aria-expanded={viewOpen}
              onClick={toggleView}
              title={viewOpen ? "Hide the description" : "Show the description"}
            >
              <span className="guide-fold" aria-hidden="true" />
              <span className="guide-kind view">Current view</span>
            </button>
          </div>
          {viewOpen && (
            <>
              <h2 className="guide-title">What you are looking at</h2>
              <p className="guide-lede">
                {describeView({
                  fieldKey: spec.key,
                  fieldLabel: spec.label.replace("Sea Water ", ""),
                  units: spec.units,
                  date: formatDate(manifest.timesteps[store.timestepIndex]),
                  fromDepth: axisToDepth(volume, store.depthFrom),
                  toDepth: axisToDepth(volume, store.depthTo),
                  exaggeration: store.exaggeration,
                  isoEnabled: store.isoEnabled,
                  isoValue: `${Math.abs(store.toValue(store.isoValue)).toFixed(1)} ${spec.units}`,
                  diverging: isDiverging(spec),
                  floatsDrawn: store.reportingByKind().floats,
                  mooringsDrawn: store.reportingByKind().moorings,
                  render: spec.render ?? "volume",
                  arrowDepth: axisToDepth(volume, morph > 0.55 ? store.depthFrom : store.surfaceLevel),
                  currentStyle: store.currentStyle,
                })}
              </p>
              <p className="guide-hint">
                Touch any control on the left and this panel explains what it does.
              </p>
            </>
          )}
        </>
      )}
    </aside>
  );
}

const KIND_LABEL: Record<string, string> = {
  science: "Changes the science",
  rendering: "Changes only how it is drawn",
  navigation: "Changes what is shown",
  view: "Current view",
};

function formatDate(stamp: string | undefined): string {
  if (!stamp) return "an unknown date";
  return new Date(stamp).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}
