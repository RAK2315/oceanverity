import type { Manifest } from "./types";

/**
 * The three bodies of water a reader actually wants the camera on, as named views.
 *
 * Getting to the Bay of Bengal took an orbit drag, a zoom and a pan, every time, and a presenter
 * doing that live in front of a room did it badly. Each of these is one press. The fourth way
 * out, back to the globe, is the dive button that is already on the bar.
 *
 * They are **camera moves only**. Nothing here touches the Field, the Timestep or the render
 * hints - that is what cyclone mode and the Explore questions are for, and a control that
 * changes four things should not sit beside three that change one. A reader who has set the
 * water up the way they want it can move around it without losing the setup.
 *
 * The distances are radii for `OceanScene.focusOn`, which hard-sets the camera rather than
 * preserving what it finds. That is the right call here and the wrong one in kiosk - see
 * `Explore.tsx`, where one question's `focusOn` framed every later question at its radius.
 * Here the reader pressed the button, so they get the framing they asked for.
 */
export interface CameraPreset {
  id: string;
  label: string;
  /** What the view is, for the button's title. */
  title: string;
  lon: number;
  lat: number;
  /** Radius for `focusOn`. Larger is further out. */
  distance: number;
}

/**
 * The presets, clipped to the region the bake actually covers.
 *
 * **"Indian EEZ" frames India's EEZ waters; it is not the baked region and it is not a
 * boundary.** The build runs 45 E to 100 E and 10 S to 25 N, which reaches the Somali coast and
 * the Andaman Sea and is a great deal more water than any EEZ - so pointing this button at the
 * middle of the box and calling it the EEZ would have been a wrong label on a correct view, in
 * a project whose whole argument is that its labels are right. Nothing here is drawn as a line
 * on the water: it is a camera position, roughly 68-94 E and 6-22 N.
 *
 * The centre of each is clamped into the region rather than typed blind, so a bake over a
 * different box cannot leave a button pointing at water that is no longer in the build.
 */
export function cameraPresets(manifest: Manifest): CameraPreset[] {
  const { west, east, south, north } = manifest.region;
  const clampLon = (lon: number) => Math.min(Math.max(lon, west + 2), east - 2);
  const clampLat = (lat: number) => Math.min(Math.max(lat, south + 2), north - 2);
  const raw: CameraPreset[] = [
    {
      id: "eez",
      label: "Indian EEZ",
      title: "India's exclusive economic zone waters, the ocean INCOIS forecasts for",
      lon: 81,
      lat: 12,
      distance: 54,
    },
    {
      id: "bay",
      label: "Bay of Bengal",
      title: "The Bay of Bengal, where the cyclones this build is about form",
      lon: 88,
      lat: 15,
      distance: 34,
    },
    {
      id: "arabian",
      label: "Arabian Sea",
      title: "The Arabian Sea, including the Somali Current in the monsoon",
      lon: 65,
      lat: 14,
      distance: 34,
    },
  ];
  return raw.map((preset) => ({
    ...preset,
    lon: clampLon(preset.lon),
    lat: clampLat(preset.lat),
  }));
}
