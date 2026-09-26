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

`ppt/script-v1-recorded.md` is the video already recorded. It is locked, so it is reported on its
own line and never counted as something to fix. `ppt/script.md` is the script for the next
recording (version 2, 2026-09-20), and it is current.

    ../.venv/Scripts/python scripts/check_figures.py          # exits 1 on a current mismatch
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "web" / "public" / "data"

WORDS = {
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty-one": 21, "twenty-three": 23, "thirty-six": 36,
    "forty-three": 43, "forty-four": 44, "forty-eight": 48,
}

CURRENT = [
    "README.md", "CONTEXT.md", "docs/README-full.md", "docs/demo", "ppt/DECK.md", "ppt/NOTES.md",
    "ppt/script.md",
    "web/index.html", "web/provenance.html", "web/requirements.html", "web/src", "scripts",
    "PRODUCT.md",
    # The probes and the capture harness. `web/src` does not reach them, and two of them
    # carried a Field count four rounds old while explaining why a check costs what it costs.
    "web/*.mjs",
]
HISTORY = [
    "CLAUDE.md", "pipeline/CLAUDE.md", "web/CLAUDE.md", "docs/adr", "docs/BUGS.md", "docs/plan",
    "pipeline/oceanverity",
    # `api/` is where the science leaves the building, and three of its module docstrings framed
    # the service around a Field count from four rounds earlier. `docs/NUMBERS.md` is the file
    # that tells everyone else to check their figures and was itself in neither list.
    "api", "pipeline/scripts", "docs/NUMBERS.md", "DESIGN.md",
]
LOCKED = ["ppt/script-v1-recorded.md"]
SUFFIXES = {".md", ".html", ".ts", ".tsx", ".py", ".mjs"}

#: Lines that match a pattern and are right, each with why. A text fragment rather than a line
#: number, so an edit above it does not silently re-point the exemption at a different line.
ALLOWED = {
    ("web/provenance.html", "steps.length + \" steps x 2 fields"): "two fields fetched per step, not the Field count",
    ("web/provenance.html", "claiming 123 tests between them"): "a comment recording the old wrong figure",
    ("web/src/store.ts", "5 to 14 moored buoys"): "a range drawn per Timestep, not the total",
    ("web/src/ui/Controls.tsx", "seventeen instruments is a small sample"): "the buoys, which are 17",
    ("web/src/ui/ProfilePanel.tsx", "twelve-step bake's 237 instruments"): "a comment about an older bake, labelled as one",
    ("ppt/script.md", "- \"Five and a half times.\""): "the 'what not to say' list, quoting version 1 so it is not repeated",
    # Added 2026-09-23 with the widened patterns below. Each is a line the new checks match and
    # that is right as written.
    ("web/src/App.tsx", 'printed as "and 0 moored'): "a sentence about an absence, quoted to say it is not printed",
    ("web/src/store.ts", "which is wrong for the 5 to 14"): "a range drawn per Timestep, wrapped onto the next line",
    ("web/src/ui/Controls.tsx", "Eleven Fields were carrying a row"): "a count of Fields at the time, in a past-tense note",
    ("ppt/DECK.md", "Zone 1 - `1  PROVIDERS"): "a diagram zone label, not a count of providers",
    ("web/index.html", "Fifteen chips of fifteen different widths"): "chips in a layout, not Fields",
    ("pipeline/oceanverity/sources/incois.py", "Twelve variables instead of four"): "INCOIS's own McCreary dataset's variable count, not ours",
    ("pipeline/oceanverity/residuals.py", "because 17"): "the buoys, which are 17",
    ("docs/plan/05-coverage-audit-and-ideas.md", "156 MB of the 192 MB total"): "a projection from the 2026-09-04 measurement above it, dated in the heading",
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


def megabytes(folder: Path) -> int:
    """The size of a folder, the way a README quotes it: decimal MB, nearest whole number."""
    return round(sum(f.stat().st_size for f in folder.rglob("*") if f.is_file()) / 1e6)


def count_in(relative: str, pattern: str) -> int:
    """How many times a pattern occurs in one source file, for a figure the bake cannot know."""
    return len(re.findall(pattern, (ROOT / relative).read_text(encoding="utf-8"), flags=re.M))


def routes(*names: str) -> int:
    """HTTP routes across some of `api/`, counted from the decorators that declare them.

    Indented, because `standards.py` and `upload.py` declare theirs inside a `register()` that
    takes the app - which is the whole point of those two being separate modules.
    """
    return sum(count_in(f"api/{name}", r"^\s*@app\.(?:get|post|delete)") for name in names)


def guide_entries() -> int:
    """How many controls `GUIDE` explains, counted the way `probe-guide.mjs` counts them."""
    source = (ROOT / "web/src/guide.ts").read_text(encoding="utf-8")
    body = source[source.index("{", source.index("GUIDE")):]
    depth = 0
    for end, character in enumerate(body):
        depth += (character == "{") - (character == "}")
        if depth == 0:
            break
    return len(re.findall(r"^  [A-Za-z_\"'][\w.\"'-]*\s*:\s*\{", body[1:end], flags=re.M))


def figures() -> list[Figure]:
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    residuals = json.loads((DATA / "residuals.json").read_text(encoding="utf-8"))
    tests = json.loads((DATA / "tests.json").read_text(encoding="utf-8"))
    by_kind = residuals["fields"]["temperature"]["byKind"]
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    probes = len([l for l in ignore if l.startswith("!web/probe-") and "pixels" not in l])
    # Every word in WORDS, longest first, so "thirty-six" is not matched as "six" would be if
    # a shorter alternative came first.
    words = "|".join(sorted(WORDS, key=len, reverse=True))
    num = rf"(\d[\d,]*(?:\.\d+)?|{words})"
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
        # Added 2026-09-23. Every one of the seven below was found written down wrong somewhere
        # by the audit in `docs/audit/2026-09-22-audit.md`, in a run of this script that
        # reported no current mismatch at all. They are the figures people quote that nothing
        # was looking for.
        Figure(
            "baked size",
            r"(\d[\d,]*(?:\.\d+)?)\s*MB\b(?=[^.\n]{0,44}(?:committed|baked|of baked data|in the build|across \d+ Timesteps|total))",
            {megabytes(DATA)},
            "size of web/public/data",
        ),
        Figure("source adapters", rf"{num}\s+(?:[Ss]ource\s+)?[Aa]dapters\b", {len(manifest["sources"]) + 1}, "manifest.sources plus the uploaded file"),
        Figure("providers", rf"{num}\s+providers\b", {len(manifest["sources"])}, "manifest.sources"),
        Figure("explained controls", rf"{num}\s+(?:explained\s+)?controls\b", {guide_entries()}, "GUIDE in web/src/guide.ts"),
        Figure("tour steps", rf"{num}\s+steps\b(?=[^.\n]{{0,34}}chapters)", {count_in("web/src/ui/Tour.tsx", r"covers:\s*\[")}, "covers: in web/src/ui/Tour.tsx"),
        Figure("explore questions", rf"{num}\s+questions\b", {count_in("web/src/explore.ts", r'^    id:\s*"')}, "the question list in web/src/explore.ts"),
        Figure("REST routes", rf"{num}\s+REST routes\b", {routes("main.py", "upload.py")}, "@app decorators in api/main.py and api/upload.py"),
        Figure("routes", rf"(?<!REST ){num}\s+routes\b", {routes("main.py", "upload.py", "standards.py")}, "@app decorators across api/"),
        # Added later the same day. The two typical-gap figures match the *value* of a comparison
        # and not the size of the pool it was taken over, so "0.18 degC across 249 floats" passed
        # on the 0.18 while the 249 had been 246 for three weeks, in five documents at once.
        Figure(
            "floats compared",
            rf"(?:across|against)\s+{num}\s+(?:real\s+|Argo\s+|drifting\s+)?floats\b",
            {by_kind["float"]["count"], manifest["drift"]["floats"]},
            "residuals byKind.float / manifest.drift.floats",
        ),
        Figure("drift cycles", rf"{num}\s+cycles\b", {manifest["drift"]["cycle"]["count"]}, "manifest.drift.cycle.count"),
    ]


#: Directories that hold generated or vendored copies of files already scanned elsewhere.
#: `web/dist` is the build output, so every figure in it is a second copy of one in `web/`
#: and would be reported twice, at line numbers nobody can edit.
SKIP_PARTS = {"node_modules", "dist", "__pycache__", ".venv"}

#: This file itself. Its `ALLOWED` table quotes the figures it checks for, so it matches its own
#: patterns on every run - nine lines of noise about its own exemption list.
SKIP_FILES = {"pipeline/scripts/check_figures.py"}


def files(roots: list[str]):
    seen = set()
    for root in roots:
        # A root may be a glob, because `web/*.mjs` is the probes and `web` is the whole build.
        matches = sorted(ROOT.glob(root)) if "*" in root else [ROOT / root]
        for path in matches:
            if path.is_file():
                candidates = [path]
            elif path.is_dir():
                candidates = sorted(path.rglob("*"))
            else:
                continue
            for child in candidates:
                if not child.is_file() or child.suffix not in SUFFIXES:
                    continue
                if SKIP_PARTS & set(child.parts) or child in seen:
                    continue
                if child.relative_to(ROOT).as_posix() in SKIP_FILES:
                    continue
                seen.add(child)
                yield child


def report(figure: Figure, match: re.Match) -> str | None:
    """The line this match should print, or None when the figure is right."""
    raw = next((g for g in match.groups() if g), match.group(0))
    value = number(raw)
    if figure.expected and value is not None and value in figure.expected:
        return None
    # A year is not a count. "The September 2026 Fields" is a date followed by a noun, and
    # widening the patterns turned every one of those into a mismatch against the Field count.
    # Only skipped where the figure could not legitimately be a year anyway.
    if value is not None and raw.isdigit() and 1900 <= value <= 2100:
        if not any(1900 <= expected <= 2100 for expected in figure.expected):
            return None
    want = ", ".join(f"{v:g}" for v in sorted(figure.expected)) or "do not quote"
    return f"{figure.name}: says {raw!r}, build says {want}  ({figure.source})"


def scan(roots: list[str], checks: list[Figure]) -> list[str]:
    found = []
    for path in files(roots):
        where = path.relative_to(ROOT).as_posix()
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for index, line in enumerate(lines):
            line_number = index + 1
            if any(where == file and fragment in line for file, fragment in ALLOWED):
                continue
            for figure in checks:
                for match in re.finditer(figure.pattern, line, flags=re.IGNORECASE):
                    message = report(figure, match)
                    if message:
                        found.append(f"{where}:{line_number}  {message}")

            # Again across the wrap. Prose in this repo is hard-wrapped at about 96 characters,
            # so "Fifteen / variables in five groups" put the number on one line and its noun on
            # the next, and a per-line scan could not see it - in `web/src`, which is a CURRENT
            # root, for a figure this file already knew how to check. Only matches that actually
            # cross the boundary are reported, so nothing is counted twice.
            if index + 1 >= len(lines):
                continue
            nxt = lines[index + 1]
            if any(where == file and fragment in nxt for file, fragment in ALLOWED):
                continue
            joined = line.rstrip() + " " + nxt.lstrip(" \t*#/|>-")
            boundary = len(line.rstrip())
            for figure in checks:
                for match in re.finditer(figure.pattern, joined, flags=re.IGNORECASE):
                    if match.start() >= boundary or match.end() <= boundary:
                        continue
                    message = report(figure, match)
                    if message:
                        found.append(f"{where}:{line_number}  {message}  (across the line wrap)")
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
