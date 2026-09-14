"""Find every figure typed into a document that no longer matches the build.

`collect_facts.py` writes what the figures *are*. This finds where they are *written down* and
disagree. It exists because on 2026-09-13 a deck audit went wrong five times in one afternoon, and
every one was a number copied from somewhere other than the build: a README, a research note, a
handoff, a screenshot of an older bake, or an estimate made in chat.

It checks a short list of figures that people actually quote, each with a pattern for how it is
written in prose, and compares what it finds with the value read from `web/public/data/`. It is
deliberately narrow: a pattern that matches loosely produces a report nobody reads.

Files are split into two kinds, because they need different action:

- **Current** - anything a reader sees today: the README, the web pages, the app's own strings,
  the deck notes. A mismatch here is a bug.
- **History** - decision records, the defect list, plans, and `CLAUDE.md`, which quote the figure
  *as it was* on purpose ("at twelve Timesteps it was nine buoys"). Listed, not failed.

`ppt/script.md` is the recorded video. It is locked, so it is reported on its own line and never
counted as something to fix.

    ../.venv/Scripts/python scripts/check_figures.py          # exits 1 on a current mismatch
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "web" / "public" / "data"

WORDS = {
    "nine": 9, "twelve": 12, "fifteen": 15, "sixteen": 16, "seventeen": 17, "thirty-six": 36,
}

CURRENT = [
    "README.md", "CONTEXT.md", "docs/README-full.md", "docs/demo", "ppt/DECK.md", "ppt/NOTES.md",
    "web/index.html", "web/provenance.html", "web/requirements.html", "web/src", "scripts",
]
HISTORY = ["CLAUDE.md", "pipeline/CLAUDE.md", "web/CLAUDE.md", "docs/adr", "docs/BUGS.md", "docs/plan", "pipeline/samudra"]
LOCKED = ["ppt/script.md"]
SUFFIXES = {".md", ".html", ".ts", ".tsx", ".py", ".mjs"}

#: Lines that match a pattern and are right, each with why. A text fragment rather than a line
#: number, so an edit above it does not silently re-point the exemption at a different line.
ALLOWED = {
    ("web/provenance.html", "steps.length + \" steps x 2 fields"): "two fields fetched per step, not the Field count",
    ("web/provenance.html", "claiming 123 tests between them"): "a comment recording the old wrong figure",
    ("web/src/store.ts", "5 to 14 moored buoys"): "a range drawn per Timestep, not the total",
    ("web/src/ui/Controls.tsx", "seventeen instruments is a small sample"): "the buoys, which are 17",
    ("web/src/ui/ProfilePanel.tsx", "twelve-step bake's 237 instruments"): "a comment about an older bake, labelled as one",
}


@dataclass
class Figure:
    name: str
    pattern: str
    expected: set[float]
    source: str


def number(text: str) -> float | None:
    text = text.lower().replace(",", "")
    if text in WORDS:
        return float(WORDS[text])
    try:
        return float(text)
    except ValueError:
        return None


def figures() -> list[Figure]:
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    residuals = json.loads((DATA / "residuals.json").read_text(encoding="utf-8"))
    tests = json.loads((DATA / "tests.json").read_text(encoding="utf-8"))
    by_kind = residuals["fields"]["temperature"]["byKind"]
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    probes = len([l for l in ignore if l.startswith("!web/probe-") and "pixels" not in l])
    num = r"(\d[\d,]*(?:\.\d+)?|nine|twelve|fifteen|sixteen|seventeen|thirty-six)"
    return [
        Figure("tests", rf"{num}\s+(?:automated\s+|pytest\s+)?tests\b|tests-{num}%20passing", {tests["total"]}, "tests.json"),
        Figure("browser probes", rf"{num}\s+(?:browser\s+|Playwright\s+)?(?:probes|browser checks)\b", {probes}, ".gitignore allowlist"),
        Figure("moored buoys", rf"{num}\s+moored buoys", {manifest["instruments"]["moorings"]}, "manifest.instruments"),
        Figure("analyses in the build", rf"{num}\s+(?:INCOIS\s+)?analyses\b|{num}\s+Timesteps\b", {len(manifest["timesteps"])}, "manifest.timesteps"),
        Figure("instruments", rf"{num}\s+(?:real\s+)?instruments\b", {manifest["floatCount"], residuals["fields"]["temperature"]["summary"]["count"]}, "manifest.floatCount / residuals count"),
        Figure("buoy typical gap", rf"{num}\s*(?:°C|degC|&deg;C)\s+(?:across|against)\s+(?:the\s+)?(?:\d+\s+)?(?:moored\s+)?buoys", {round(by_kind["mooring"]["meanAbsBias"], 2), round(by_kind["mooring"]["meanAbsBias"], 1)}, "residuals byKind.mooring"),
        Figure("float typical gap", rf"{num}\s*(?:°C|degC|&deg;C)\s+(?:across|against)\s+(?:the\s+)?(?:\d+\s+)?(?:Argo\s+)?floats", {round(by_kind["float"]["meanAbsBias"], 2), round(by_kind["float"]["meanAbsBias"], 1)}, "residuals byKind.float"),
        Figure("floats-to-buoys ratio", r"(five and a half|5\.5)\s*(?:x|×|times)", set(), "not like for like: floats compared to ~2000 m, buoys to 500 m"),
        Figure("coverage gap", rf"{num}\s*%\s+of\s+(?:the\s+)?(?:mapped ocean|block|this block)", {round(manifest["coverage"]["emptyFraction"] * 100, 1)}, "manifest.coverage.emptyFraction"),
        Figure("drift floats", rf"{num}\s+(?:real\s+|Argo\s+)?floats[':,\s][^.\n]{{0,40}}(?:median\s+\d+(?:\.\d+)?\s*km|own positions|scored|its error)", {manifest["drift"]["floats"]}, "manifest.drift.floats"),
        Figure("window length", r"(four|five|twelve)\s+months", set(), f"the window is {len(manifest['timesteps'])} ten-day analyses, about a year"),
        Figure("variables", rf"{num}\s+(?:variables|Fields)\b", {len(manifest["fields"])}, "manifest.fields"),
    ]


def files(roots: list[str]):
    for root in roots:
        path = ROOT / root
        if path.is_file():
            yield path
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix in SUFFIXES and "node_modules" not in child.parts:
                    yield child


def scan(roots: list[str], checks: list[Figure]) -> list[str]:
    found = []
    for path in files(roots):
        where = path.relative_to(ROOT).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if any(where == file and fragment in line for file, fragment in ALLOWED):
                continue
            for figure in checks:
                for match in re.finditer(figure.pattern, line, flags=re.IGNORECASE):
                    raw = next((g for g in match.groups() if g), match.group(0))
                    value = number(raw)
                    if figure.expected and value is not None and value in figure.expected:
                        continue
                    want = ", ".join(f"{v:g}" for v in sorted(figure.expected)) or "do not quote"
                    found.append(f"{where}:{line_number}  {figure.name}: says {raw!r}, build says {want}  ({figure.source})")
    return found


def main() -> int:
    checks = figures()
    current = scan(CURRENT, checks)
    history = scan(HISTORY, checks)
    locked = scan(LOCKED, checks)
    print(f"CURRENT - a reader sees these today, fix them ({len(current)}):")
    for line in current:
        print(f"  {line}")
    print(f"\nHISTORY - quoted as it was, listed only ({len(history)}):")
    for line in history:
        print(f"  {line}")
    print(f"\nLOCKED - the recorded video, not to be changed ({len(locked)}):")
    for line in locked:
        print(f"  {line}")
    return 1 if current else 0


if __name__ == "__main__":
    raise SystemExit(main())
