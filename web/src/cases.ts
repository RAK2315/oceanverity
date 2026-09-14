/**
 * A real storm, walked through with the controls the platform already has.
 *
 * Every feature here was built as its own demo, and a forecaster does not think in features:
 * they think in events. Severe Cyclonic Storm Montha crossed the Bay of Bengal inside this build's
 * window, so this is the same heat potential, temperature, moored buoy and drift a user could
 * reach by hand, set up one after another on the dates it happened.
 *
 * **No figure is typed here.** Every number comes from `data/cases/montha.json`, which
 * `pipeline/scripts/build_montha_case.py` measures from IMD's best track and the build's own
 * Grids. That is `guide.ts`'s `{token}` rule applied to a whole feature.
 *
 * **Three things it never says**, each for a reason measured when it was written:
 *
 * - That the buoy it shows was under the storm. The nearest moored buoy is a few hundred
 *   kilometres from IMD's track, and the step says how many. Argo floats did surface near the
 *   track, and the step says that too.
 * - That the storm caused a change. The analyses are ten days apart, so the change near the track
 *   is always shown beside the change far from it, in the same bay over the same ten days.
 * - That a float's chart is from October. A float's comparison is from its newest cast.
 *
 * Touching any control ends it, the same rule as the tour, enforced in `store.set`.
 */

import { useStore } from "./store";
import type { ExploreHelpers } from "./explore";

export interface StormBand {
  cells: number;
  medianBefore: number;
  medianAfter: number;
  shareIncreased: number;
}

export interface StormCase {
  id: string;
  name: string;
  grade: string;
  basin: string;
  source: { who: string; what: string; url: string; file: string };
  track: { time: string; lat: number; lon: number; grade: string; windKt: number }[];
  peakWindKt: number;
  formed: string;
  lastFix: string;
  landfall: { lat: number; lon: number; place: string; day: string; note: string };
  steps: { before: number; after: number; beforeTime: string; afterTime: string };
  method: { nearKm: number; farKm: number };
  changes: Record<
    "mixedLayerDepth" | "d26" | "heatPotential" | "temperature5m",
    { units: string; near: StormBand; far: StormBand; depthMetres?: number }
  >;
  buoys: {
    id: string;
    lat: number;
    lon: number;
    distanceKm: number;
    depthMetres: number;
    measuredChange: number;
    analysedChange: number;
  }[];
  floats: { id: string; distanceKm: number }[];
  /** The water node nearest the landfall with a current under it, chosen by the pipeline. */
  driftPin: { lon: number; lat: number; kmFromLandfall: number; days: number };
}

export interface CaseStep {
  title: string;
  body: string;
  /** A short plain note on the limit, where one matters. Not a warning box. */
  caution?: string;
  enter: (helpers: ExploreHelpers) => void;
}

const store = useStore;

/** The same clean start every Explore question gets, so no step inherits the last one's panel. */
function calm(): void {
  store.setState({
    selectedFloatId: null,
    selectedAnomaly: null,
    isolateAnomaly: false,
    biasMode: false,
    driftPin: null,
    placingDriftPin: false,
    placingSection: 0,
    sectionFrom: null,
    sectionTo: null,
    showDriftCheck: false,
    playing: false,
    isoEnabled: false,
    showAnomalies: false,
    touched: null,
  });
}

const day = (stamp: string) =>
  new Date(stamp).toLocaleDateString("en-GB", { day: "numeric", month: "long", timeZone: "UTC" });
const one = (value: number) => value.toFixed(1);
const whole = (value: number) => Math.round(value).toString();

/** Where the track sits, for panning: the middle of IMD's fixes. */
function trackCentre(c: StormCase): [number, number] {
  const lons = c.track.map((f) => f.lon);
  const lats = c.track.map((f) => f.lat);
  return [(Math.min(...lons) + Math.max(...lons)) / 2, (Math.min(...lats) + Math.max(...lats)) / 2];
}

export function buildCaseSteps(c: StormCase, dive: (into: boolean) => void): CaseStep[] {
  const { before, after, beforeTime, afterTime } = c.steps;
  const heat = c.changes.heatPotential;
  const surface = c.changes.temperature5m;
  const d26 = c.changes.d26;
  const buoy = c.buoys[0];
  const [lon, lat] = trackCentre(c);
  const kmh = Math.round((c.peakWindKt * 1.852) / 5) * 5;
  const inVolume = () => store.getState().morph > 0.5;
  const daysBefore = Math.round((Date.parse(c.formed) - Date.parse(beforeTime)) / 86400000);
  const nearestFloat = c.floats[0];

  const steps: CaseStep[] = [
    {
      title: `Cyclone ${c.name}, ${new Date(c.formed).getUTCFullYear()}`,
      body:
        `The pink line is IMD's official track. ${c.name} formed in the ${c.basin} on` +
        ` ${day(c.formed)} and reached the coast near ${c.landfall.place} on ${c.landfall.day},` +
        ` with winds up to ${kmh} km/h.`,
      enter: (helpers) => {
        calm();
        store.getState().selectField("temperature");
        store.setState({ timestepIndex: before });
        if (!inVolume()) dive(true);
        helpers.panTo(lon, lat);
      },
    },
    {
      title: `The fuel waiting for it`,
      body:
        `On ${day(beforeTime)}, ${daysBefore} days before it formed, the water along its path held` +
        ` ${whole(heat.near.medianBefore)} kJ/cm² of heat - the energy a cyclone feeds on.`,
      enter: (helpers) => {
        calm();
        store.getState().selectField("heat_potential");
        store.setState({ timestepIndex: before });
        helpers.panTo(lon, lat);
      },
    },
    {
      title: `How deep the warm water ran`,
      body:
        `The sheet is where the water drops below 26 °C. Along the path it sat about` +
        ` ${whole(d26.near.medianBefore)} m down. A deep warm layer is hard for a storm to stir` +
        ` away, so it keeps feeding it. By ${day(afterTime)} it had thinned to about` +
        ` ${whole(d26.near.medianAfter)} m.`,
      enter: (helpers) => {
        calm();
        store.getState().selectField("d26");
        store.setState({ timestepIndex: before });
        helpers.panTo(lon, lat);
      },
    },
    {
      title: `The storm drew the heat out`,
      body:
        `By ${day(afterTime)} the heat along its path had fallen to ${whole(heat.near.medianAfter)} kJ/cm².` +
        ` Away from the path, the same bay rose from ${whole(heat.far.medianBefore)} to` +
        ` ${whole(heat.far.medianAfter)}, so the drop follows the storm, not the season.`,
      caution: "Analyses are ten days apart.",
      enter: (helpers) => {
        calm();
        store.getState().selectField("heat_potential");
        store.setState({ timestepIndex: after });
        helpers.panTo(lon, lat);
      },
    },
    {
      title: "A cold wake behind it",
      body:
        `The sea surface along its path cooled from ${one(surface.near.medianBefore)} to` +
        ` ${one(surface.near.medianAfter)} °C, while water away from it did not.`,
      enter: (helpers) => {
        calm();
        store.getState().selectField("temperature");
        store.setState({ timestepIndex: after });
        helpers.panTo(lon, lat);
      },
    },
  ];

  if (buoy) {
    steps.push({
      title: `An instrument that felt it`,
      body:
        `Moored buoy ${buoy.id}, ${whole(buoy.distanceKm)} km from the path, measured its water ${buoy.measuredChange < 0 ? "cool" : "warm"} by` +
        ` ${one(Math.abs(buoy.measuredChange))} °C at ${whole(buoy.depthMetres)} m. Its chart is open on the right.`,
      caution: nearestFloat
        ? `Argo floats surfaced even closer, ${whole(nearestFloat.distanceKm)} km from the path.`
        : undefined,
      enter: (helpers) => {
        calm();
        store.getState().selectField("temperature");
        store.setState({ timestepIndex: after, selectedFloatId: buoy.id });
        helpers.panTo(buoy.lon, buoy.lat);
      },
    });
  }

  steps.push({
    title: "Where would something adrift go?",
    body:
      `A pin dropped off the coast, south of where ${c.name} came ashore, rides the analysed currents for` +
      ` ${whole(c.driftPin.days)} days. The same method is scored against real floats.`,
    caution: "Currents only, without wind or waves.",
    enter: (helpers) => {
      calm();
      store.getState().selectField("current_speed");
      const pin = { lon: c.driftPin.lon, lat: c.driftPin.lat };
      store.setState((state) => ({
        timestepIndex: after,
        driftPin: pin,
        driftDays: c.driftPin.days,
        openGroups: { ...state.openGroups, drift: true },
      }));
      helpers.panTo(pin.lon, pin.lat);
    },
  });

  return steps;
}
