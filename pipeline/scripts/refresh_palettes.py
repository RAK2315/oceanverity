"""Rewrite the shipped manifest's `palettes` block from `samudra.palettes`, and nothing else.

The colourbar switcher needs alternates that a bake produced before it existed does not carry.
A full `python -m samudra.bake` would produce them, but it also re-fetches INCOIS, Argo and
Copernicus - a network round trip, a credential, and a whole new set of numbers - to change a
lookup table that is a pure function of `AVAILABLE`.

So this does the narrow thing. It reads `web/public/data/manifest.json`, replaces the value at
`palettes` with what the pipeline would write today, and leaves every other key byte for byte as
it was. `coverage` is preserved from the existing manifest rather than rebuilt, because its band
edges are expressed in the encoded range *that bake* produced and a table built against a
different range would draw its steps in the wrong places.

This is the same standing as `collect_tests.py`: generated data stays generated, written by the
pipeline, never hand-edited. Running the real bake afterwards produces the same block.

    ../.venv/Scripts/python scripts/refresh_palettes.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from samudra.palettes import AVAILABLE, all_tables  # noqa: E402

MANIFEST = Path(__file__).resolve().parents[2] / "web" / "public" / "data" / "manifest.json"


def main() -> int:
    if not MANIFEST.exists():
        print(f"no manifest at {MANIFEST}", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    before = set(manifest.get("palettes", {}))

    # The banded coverage table belongs to the bake that made it: its edges are positions in
    # that bake's encoded range. Carry it across untouched rather than regenerating it blind.
    coverage = manifest.get("palettes", {}).get("coverage")
    palettes = all_tables()
    if coverage is not None:
        palettes["coverage"] = coverage

    manifest["palettes"] = palettes
    MANIFEST.write_text(json.dumps(manifest), encoding="utf-8")

    after = set(palettes)
    added = sorted(after - before)
    removed = sorted(before - after)
    print(f"{len(after)} palettes written to {MANIFEST.name}")
    if added:
        print(f"  added:   {', '.join(added)}")
    if removed:
        print(f"  removed: {', '.join(removed)}")
    missing = [name for name in AVAILABLE if name not in after]
    if missing:
        print(f"  MISSING: {', '.join(missing)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
