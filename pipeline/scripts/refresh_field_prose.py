"""Rewrite the shipped manifest's Field *prose* from the `FieldSpec` declarations, and nothing else.

A Field's label, units and description are written by hand in `bake.py` and are pure text: they
are not measured, they do not depend on which Timesteps were fetched, and a bake produces
exactly the same string every time. Everything else in a Field's manifest entry - `range` above
all - is a reading off the data and belongs to the bake that took it.

So when a sentence in `bake.py` is corrected after a bake has run, the manifest carries the old
one until somebody spends thirty-six minutes and a Copernicus credential re-fetching numbers
that were already right. That happened: `temperature_normal_anomaly`'s description said the
Temperature Anomaly beside it was "a departure from this bake's own **four months**" against a
bake of a year, and the one place that string reaches a reader is a WMS layer's `<Abstract>`,
where a consumer cannot see it came from a bake that is gone.

This does the narrow thing, exactly as `refresh_palettes.py` does for the palette tables. It
matches each manifest Field to its `FieldSpec` **by key**, rewrites only the prose keys, and
leaves every other byte alone - including the order of the list and any Field the specs do not
know about, which is reported rather than removed. Running the real bake afterwards produces
the same strings.

Generated data stays generated, written by the pipeline, never hand-edited.

    ../.venv/Scripts/python scripts/refresh_field_prose.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from oceanverity.bake import all_field_specs  # noqa: E402

MANIFEST = Path(__file__).resolve().parents[2] / "web" / "public" / "data" / "manifest.json"

# The keys that are prose. `range` is a measurement and is not here; neither are `palette`,
# `display_min`, `display_max`, `emphasis`, `opacity`, `isosurface`, `render` or `group`, which
# are declarations the frontend acts on rather than sentences a reader reads - moving one of
# those without a bake would put the manifest out of step with the data beside it.
PROSE = ("label", "units", "description")


def main() -> int:
    if not MANIFEST.exists():
        print(f"no manifest at {MANIFEST}", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    specs = {spec.key: spec for spec in all_field_specs()}

    changed: list[str] = []
    unknown: list[str] = []
    for entry in manifest.get("fields", []):
        spec = specs.get(entry["key"])
        if spec is None:
            unknown.append(entry["key"])
            continue
        for key in PROSE:
            fresh = getattr(spec, key)
            if entry.get(key) != fresh:
                changed.append(f"{entry['key']}.{key}")
                entry[key] = fresh

    MANIFEST.write_text(json.dumps(manifest), encoding="utf-8")

    print(f"{len(manifest.get('fields', []))} fields checked in {MANIFEST.name}")
    if changed:
        for name in changed:
            print(f"  rewritten: {name}")
    else:
        print("  nothing to rewrite; the manifest's prose already matches the specs")
    if unknown:
        print(f"  no spec for: {', '.join(unknown)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
