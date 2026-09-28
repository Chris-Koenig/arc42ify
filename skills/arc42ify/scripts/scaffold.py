#!/usr/bin/env python3
"""
scaffold.py — creates the docs/arc42/ folder structure inside a target repo.

Usage:
    python3 scaffold.py /path/to/target-repo [--lang de|en]

Creates:
    docs/arc42/00-index.md
    docs/arc42/01-einfuehrung-und-ziele.md
    ... one file per arc42 chapter ...
    docs/arc42/12-glossar.md
    docs/arc42/assets/diagrams/   (empty, .svg files go here)

Idempotent: existing files are never overwritten, so re-running after the
agent has already filled some chapters in is safe.
"""
import argparse
import os
import sys

CHAPTERS_DE = [
    ("00-index", "arc42-Dokumentation", None),
    ("01-einfuehrung-und-ziele", "1. Einführung und Ziele", None),
    ("02-randbedingungen", "2. Randbedingungen", None),
    ("03-kontextabgrenzung", "3. Kontextabgrenzung", "boxes"),
    ("04-loesungsstrategie", "4. Lösungsstrategie", None),
    ("05-bausteinsicht", "5. Bausteinsicht", "boxes"),
    ("06-laufzeitsicht", "6. Laufzeitsicht", "sequence"),
    ("07-verteilungssicht", "7. Verteilungssicht", "boxes"),
    ("08-querschnittliche-konzepte", "8. Querschnittliche Konzepte", "layers"),
    ("09-architekturentscheidungen", "9. Architekturentscheidungen", None),
    ("10-qualitaetsanforderungen", "10. Qualitätsanforderungen", None),
    ("11-risiken-und-technische-schulden", "11. Risiken und technische Schulden", None),
    ("12-glossar", "12. Glossar", None),
]

CHAPTERS_EN = [
    ("00-index", "arc42 Documentation", None),
    ("01-introduction-and-goals", "1. Introduction and Goals", None),
    ("02-constraints", "2. Architecture Constraints", None),
    ("03-context-and-scope", "3. Context and Scope", "boxes"),
    ("04-solution-strategy", "4. Solution Strategy", None),
    ("05-building-block-view", "5. Building Block View", "boxes"),
    ("06-runtime-view", "6. Runtime View", "sequence"),
    ("07-deployment-view", "7. Deployment View", "boxes"),
    ("08-crosscutting-concepts", "8. Crosscutting Concepts", "layers"),
    ("09-architecture-decisions", "9. Architecture Decisions", None),
    ("10-quality-requirements", "10. Quality Requirements", None),
    ("11-risks-and-technical-debt", "11. Risks and Technical Debt", None),
    ("12-glossary", "12. Glossary", None),
]

# The scripts live in the skill folder, not in the target repo, so the index
# names them without a path that would only resolve inside the skill.
INDEX_BODY_DE = """> Diese Dokumentation folgt [arc42](https://arc42.de/). Erzeugt und
> gepflegt mit dem `arc42ify`-Skill. Diagramme liegen als SVG unter
> `assets/diagrams/`, jeweils neben der `*.diagram.json`-Spec, aus der sie
> entstehen. Geändert wird immer die Spec; danach mit `render_diagram.py`
> neu rendern und mit `self_check.py` prüfen — beide liegen im Ordner
> `scripts/` des Skills (z. B. `.claude/skills/arc42ify/scripts/`).

| Kapitel | Status |
|---|---|
{toc}
"""

INDEX_BODY_EN = """> This documentation follows [arc42](https://arc42.org/). Generated and
> maintained with the `arc42ify` skill. Diagrams live as SVG under
> `assets/diagrams/`, next to the `*.diagram.json` spec they are rendered
> from. Always change the spec, then re-render with `render_diagram.py` and
> check with `self_check.py` — both live in the skill's `scripts/` folder
> (e.g. `.claude/skills/arc42ify/scripts/`).

| Chapter | Status |
|---|---|
{toc}
"""

# Status values match SKILL.md: vollständig/Entwurf/TODO (complete/draft/TODO).
CHAPTER_STUB_DE = """<!-- status: TODO -->

_TODO: wird vom arc42ify-Skill ausgefüllt. Was in dieses Kapitel gehört und
wo es im Code steht, beschreibt references/arc42-sections.md im Skill._
"""

CHAPTER_STUB_EN = """<!-- status: TODO -->

_TODO: filled in by the arc42ify agent skill. See
references/arc42-sections.md in the skill for what belongs in this chapter
and where to find it in this codebase._
"""


def write_if_missing(path, content):
    if os.path.exists(path):
        print(f"skip (exists): {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"created: {path}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")  # e.g. a cp1252 console on Windows
    ap = argparse.ArgumentParser()
    ap.add_argument("target_repo")
    ap.add_argument("--lang", choices=["de", "en"], default="de")
    args = ap.parse_args()

    chapters = CHAPTERS_DE if args.lang == "de" else CHAPTERS_EN
    index_body = INDEX_BODY_DE if args.lang == "de" else INDEX_BODY_EN
    chapter_stub = CHAPTER_STUB_DE if args.lang == "de" else CHAPTER_STUB_EN

    base = os.path.join(args.target_repo, "docs", "arc42")
    os.makedirs(os.path.join(base, "assets", "diagrams"), exist_ok=True)

    toc_lines = []
    for slug, title, _diagram_kind in chapters[1:]:
        toc_lines.append(f"| [{title}]({slug}.md) | TODO |")
        write_if_missing(os.path.join(base, f"{slug}.md"), f"# {title}\n\n{chapter_stub}")

    index_slug, index_title, _ = chapters[0]
    write_if_missing(
        os.path.join(base, f"{index_slug}.md"),
        f"# {index_title}\n\n" + index_body.format(toc="\n".join(toc_lines)),
    )

    gitkeep = os.path.join(base, "assets", "diagrams", ".gitkeep")
    if not os.path.exists(gitkeep):
        open(gitkeep, "w").close()

    print(f"\ndocs/arc42/ ready under {base}")


if __name__ == "__main__":
    main()
