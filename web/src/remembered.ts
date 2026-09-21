/**
 * The four things this console remembers per browser: the theme, the guide description's fold,
 * the map key's fold, and where the map key was dragged to.
 *
 * They were stored under a `samudra.` prefix until the project was renamed on 2026-09-20.
 * Renaming a key outright is not free - it silently forgets what a returning reader chose, and
 * the reader has no way to know why their light theme went dark. So a read falls back to the
 * old prefix once and the next write moves the value forward under the new one.
 *
 * The three static pages carry their own inline copy of this for the theme alone, because they
 * have to set `data-theme` before first paint and cannot wait for a module. `capture.mjs` and
 * `probe-landing.mjs` write the theme key directly for the same reason, so all four copies of
 * the string move together or a screenshot run quietly gets the wrong theme.
 */

const PREFIX = "oceanverity.";
const LEGACY_PREFIX = "samudra.";

/** The stored value, from the new key or failing that the old one. Null if neither is set. */
export function remembered(key: string): string | null {
  try {
    const current = window.localStorage.getItem(PREFIX + key);
    if (current !== null) return current;
    return window.localStorage.getItem(LEGACY_PREFIX + key);
  } catch {
    // A private window that refuses storage is not an error; it simply remembers nothing.
    return null;
  }
}

/** Store under the new key, and drop the old one so the fallback stops firing. */
export function remember(key: string, value: string): void {
  try {
    window.localStorage.setItem(PREFIX + key, value);
    window.localStorage.removeItem(LEGACY_PREFIX + key);
  } catch {
    // Failing to remember must never cost the control that was just used.
  }
}

/** Forget both copies, for a control that resets itself. */
export function forget(key: string): void {
  try {
    window.localStorage.removeItem(PREFIX + key);
    window.localStorage.removeItem(LEGACY_PREFIX + key);
  } catch {
    // As above.
  }
}
