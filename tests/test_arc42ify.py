"""
Tests for arc42ify: the shipped diagrams, the edge router, the checker (in
both directions: broken input must be reported, good input must pass), the
command-line scripts, the scaffold, the skill metadata and the plugin
manifests.

Standard library only. From the repo root:
    python3 -m unittest discover -s tests -v
"""
import ast
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "arc42ify")
SCRIPTS = os.path.join(SKILL, "scripts")
FIXTURES = os.path.join(ROOT, "tests", "fixtures")

sys.path.insert(0, SCRIPTS)
import render_diagram as rd  # noqa: E402
import self_check as sc  # noqa: E402


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def shipped_diagrams():
    """(spec, committed svg) for the templates and the docs example."""
    pairs = [(s, s[:-len(".json")] + ".svg")
             for s in sorted(glob.glob(os.path.join(SKILL, "assets", "templates", "*.json")))]
    pairs += [(s, s[:-len(".diagram.json")] + ".svg")
              for s in sorted(glob.glob(os.path.join(
                  ROOT, "docs-example", "docs", "arc42", "assets", "diagrams", "*.diagram.json")))]
    return pairs


def pass_fixtures():
    return sorted(glob.glob(os.path.join(FIXTURES, "pass", "*.json")))


def all_good_specs():
    return [s for s, _ in shipped_diagrams()] + pass_fixtures()


def run_script(name, *args, env=None):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, name), *args],
                          capture_output=True, env=env, cwd=ROOT)


class ShippedDiagrams(unittest.TestCase):

    def test_found_all_diagrams(self):
        self.assertGreaterEqual(len(shipped_diagrams()), 12)

    def test_specs_pass_self_check(self):
        for spec_path, _ in shipped_diagrams():
            with self.subTest(spec=rel(spec_path)):
                self.assertEqual(sc.check(load(spec_path)), [])

    def test_committed_svgs_match_a_fresh_render(self):
        for spec_path, svg_path in shipped_diagrams():
            with self.subTest(svg=rel(svg_path)):
                with open(svg_path, encoding="utf-8", newline="") as f:
                    committed = f.read()
                self.assertTrue(
                    committed == rd.render_svg(load(spec_path)),
                    f"stale SVG, re-render it: python3 skills/arc42ify/scripts/render_diagram.py "
                    f"{rel(spec_path)} {rel(svg_path)}")
                self.assertEqual(sc.check_svg(committed), [])


class Router(unittest.TestCase):

    def boxes_layouts(self):
        for path in all_good_specs():
            spec = load(path)
            if spec["kind"] == "boxes":
                yield rel(path), rd.layout_boxes(spec)

    def test_edges_are_orthogonal_and_start_and_end_on_their_boxes(self):
        for name, lay in self.boxes_layouts():
            for e in lay["edges"]:
                with self.subTest(spec=name, edge=f"{e['from']}->{e['to']}"):
                    pts = e["points"]
                    for a, b in rd.segments(pts):
                        self.assertTrue(a[0] == b[0] or a[1] == b[1], f"diagonal segment {a}-{b}")
                    self.assertTrue(_on_border(pts[0], lay["boxes"][e["from"]]))
                    self.assertTrue(_on_border(pts[-1], lay["boxes"][e["to"]]))

    def test_edges_keep_clear_of_other_boxes(self):
        clearance = 2 * rd.STEP - 1
        for name, lay in self.boxes_layouts():
            for e in lay["edges"]:
                for nid, r in lay["boxes"].items():
                    if nid in (e["from"], e["to"]):
                        continue
                    with self.subTest(spec=name, edge=f"{e['from']}->{e['to']}", node=nid):
                        self.assertFalse(any(rd.segment_hits_rect(a, b, r, clearance)
                                             for a, b in rd.segments(e["points"])))

    def test_every_edge_end_has_its_own_port(self):
        for name, lay in self.boxes_layouts():
            with self.subTest(spec=name):
                ends = [p for e in lay["edges"] for p in (e["points"][0], e["points"][-1])]
                self.assertEqual(len(ends), len(set(ends)))

    def test_shapes_sit_on_the_4px_grid(self):
        shape = re.compile(r'<(rect|line|path)\b([^>]*)>')
        coord = re.compile(r'(?:^|\s)(x|y|x1|y1|x2|y2|width|height)="(-?[\d.]+)"')
        for path in all_good_specs():
            svg = rd.render_svg(load(path))
            body = svg.split("</defs>", 1)[1]
            with self.subTest(spec=rel(path)):
                for _, attrs in shape.findall(body):
                    values = [float(v) for _, v in coord.findall(attrs)]
                    d = re.search(r'(?:^|\s)d="([^"]*)"', attrs)
                    if d:
                        values += [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d.group(1))]
                    for v in values:
                        self.assertEqual(v % rd.GRID, 0, f"{v} is off the grid in {attrs.strip()}")


def _on_border(p, rect):
    x, y, w, h = rect
    on_x = p[0] in (x, x + w) and y <= p[1] <= y + h
    on_y = p[1] in (y, y + h) and x <= p[0] <= x + w
    return on_x or on_y


class CheckerCatchesDefects(unittest.TestCase):
    """Every checker rule is tested with input that must fail, and the good
    fixtures prove the same rules stay quiet on valid diagrams."""

    EXPECTED = {
        "boxes-label-too-long.json": "overlaps node 'a'",
        "boxes-nodes-overlap.json": "nodes 'b' and 'd' overlap",
        "boxes-group-swallows-node.json": "overlaps node 'b', which is not a member",
        "boxes-unknown-edge-target.json": "unknown 'to': 'zzz'",
        "boxes-too-many-focal.json": "3 focal nodes",
        "boxes-node-label-too-wide.json": "label of node 'c' is wider than its box",
        "sequence-label-wider-than-gap.json": "wider than the gap between two lanes",
        "sequence-self-call-runs-into-lane.json": "runs into the next lane",
        "sequence-lane-label-too-wide.json": "label of lane 'a' is wider than its header box",
        "layers-items-too-wide.json": "items of layer 'Everything' are wider than the layer",
    }

    def test_every_fail_fixture_has_an_expectation(self):
        found = {os.path.basename(p) for p in glob.glob(os.path.join(FIXTURES, "fail", "*.json"))}
        self.assertEqual(found, set(self.EXPECTED))

    def test_fail_fixtures_are_reported(self):
        for name, expected in self.EXPECTED.items():
            with self.subTest(fixture=name):
                problems = sc.check(load(os.path.join(FIXTURES, "fail", name)))
                self.assertTrue(any(expected in p for p in problems),
                                f"expected {expected!r} in {problems}")

    def test_pass_fixtures_are_clean(self):
        for path in pass_fixtures():
            with self.subTest(fixture=rel(path)):
                self.assertEqual(sc.check(load(path)), [])

    def test_geometry_the_old_renderer_produced_is_reported(self):
        # The router can no longer produce these defects, so feed the checker
        # hand-made geometry: an edge straight through a box, a label sitting
        # on another edge, and two edges drawn on top of each other.
        spec = {"kind": "boxes", "nodes": [
            {"id": "a", "label": "A", "col": 0, "row": 0},
            {"id": "b", "label": "B", "col": 0, "row": 1},
            {"id": "c", "label": "C", "col": 0, "row": 2}]}
        boxes = {"a": (0, 0, 192, 72), "b": (0, 144, 192, 72), "c": (0, 288, 192, 72)}

        def edge(src, dst, points, label=None, rect=None):
            return {"from": src, "to": dst, "points": points, "label_rect": rect,
                    "label_seg": 0 if rect else None,
                    "spec": {"from": src, "to": dst, "label": label} if label else {"from": src, "to": dst}}

        broken = {"boxes": boxes, "groups": [], "bounds": None, "edges": [
            edge("a", "b", [(108, 72), (108, 144)], "calls", (76, 100, 64, 16)),
            edge("a", "c", [(84, 72), (84, 288)]),
            edge("c", "a", [(84, 288), (84, 72)]),
        ]}
        with mock.patch.object(rd, "layout_boxes", return_value=broken):
            problems = "\n".join(sc.check_boxes_geometry(spec))
        self.assertIn("edge a->c runs through node 'b'", problems)
        self.assertIn("label 'calls' of edge a->b sits on top of edge a->c", problems)
        self.assertIn("edges a->c and c->a run on top of each other", problems)


class CommandLine(unittest.TestCase):

    def test_render_then_check_round_trip(self):
        spec = os.path.join(SKILL, "assets", "templates", "context-diagram.json")
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "nested", "context.svg")
            r = run_script("render_diagram.py", spec, out)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = run_script("self_check.py", spec, out)
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn(b"OK", r.stdout)

    def test_failures_exit_1_even_on_a_console_that_cannot_print_the_label(self):
        # The label contains "→", which cp1252 (a common Windows console
        # encoding) cannot encode. The check must still report, not crash.
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        r = run_script("self_check.py", os.path.join(FIXTURES, "fail", "boxes-label-too-long.json"), env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn(b"FAIL", r.stdout)
        self.assertNotIn(b"Traceback", r.stderr)

    def test_scripts_without_arguments_print_usage(self):
        for script in ("render_diagram.py", "self_check.py"):
            with self.subTest(script=script):
                r = run_script(script)
                self.assertEqual(r.returncode, 1)
                self.assertIn(b"Usage", r.stdout)


class Scaffold(unittest.TestCase):

    def test_creates_index_twelve_chapters_and_diagram_folder(self):
        for lang in ("de", "en"):
            with self.subTest(lang=lang), tempfile.TemporaryDirectory() as tmp:
                r = run_script("scaffold.py", tmp, "--lang", lang)
                self.assertEqual(r.returncode, 0, r.stderr)
                base = os.path.join(tmp, "docs", "arc42")
                chapters = sorted(f for f in os.listdir(base) if f.endswith(".md"))
                self.assertEqual(len(chapters), 13)
                self.assertTrue(chapters[0].startswith("00-"))
                self.assertTrue(os.path.isfile(os.path.join(base, "assets", "diagrams", ".gitkeep")))

    def test_never_overwrites_existing_chapters(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_script("scaffold.py", tmp, "--lang", "de")
            chapter = glob.glob(os.path.join(tmp, "docs", "arc42", "03-*.md"))[0]
            with open(chapter, "w", encoding="utf-8") as f:
                f.write("# hand-written\n")
            r = run_script("scaffold.py", tmp, "--lang", "de")
            self.assertIn(b"skip (exists)", r.stdout)
            with open(chapter, encoding="utf-8") as f:
                self.assertEqual(f.read(), "# hand-written\n")


def frontmatter():
    with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as f:
        text = f.read()
    head = text.split("---", 2)[1]
    fields = dict(line.split(": ", 1) for line in head.strip().splitlines())
    return fields, text


class SkillMetadata(unittest.TestCase):
    """The description is the only text an agent sees before it decides to
    load the skill, so its trigger words are guarded here."""

    TRIGGERS = [
        "arc42", "docs/arc42/",
        "Architekturdoku", "dokumentiere die Architektur",
        "Kontextabgrenzung", "Bausteinsicht", "Laufzeitsicht", "Verteilungssicht",
        "architecture documentation", "document the architecture",
        "context view", "building block view", "runtime view", "deployment view",
        "architecture decisions", "quality requirements", "technical debt",
    ]

    def test_name_follows_the_agent_skills_spec(self):
        fields, _ = frontmatter()
        self.assertEqual(fields["name"], os.path.basename(SKILL))
        self.assertRegex(fields["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(fields["name"]), 64)

    def test_description_fits_and_is_valid_plain_yaml(self):
        fields, _ = frontmatter()
        d = fields["description"]
        self.assertLessEqual(len(d), 1024)
        self.assertLessEqual(len(fields.get("compatibility", "")), 500)
        self.assertNotIn(": ", d, "': ' ends a plain YAML value; rephrase or quote it")
        self.assertNotIn(" #", d, "' #' starts a YAML comment")

    def test_description_keeps_its_trigger_words(self):
        fields, _ = frontmatter()
        for word in self.TRIGGERS:
            with self.subTest(word=word):
                self.assertIn(word, fields["description"])

    def test_skill_md_stays_under_500_lines(self):
        _, text = frontmatter()
        self.assertLess(len(text.splitlines()), 500)


class PluginManifests(unittest.TestCase):
    """Claude Code, Copilot and Codex read their own manifest, but all of
    them install the same skills/ folder. The shared identity must not drift."""

    SHARED = ("name", "version", "description", "author", "homepage",
              "repository", "license", "keywords")

    def setUp(self):
        self.claude = load(os.path.join(ROOT, ".claude-plugin", "plugin.json"))
        self.codex = load(os.path.join(ROOT, ".codex-plugin", "plugin.json"))

    def test_manifests_share_one_identity(self):
        for key in self.SHARED:
            with self.subTest(field=key):
                self.assertEqual(self.claude[key], self.codex[key])
        self.assertEqual(self.claude["name"], os.path.basename(SKILL))

    def test_marketplaces_list_the_plugin_at_the_repo_root(self):
        claude_mp = load(os.path.join(ROOT, ".claude-plugin", "marketplace.json"))
        entry = claude_mp["plugins"][0]
        self.assertEqual(entry["name"], self.claude["name"])
        self.assertEqual(entry["source"], "./")
        self.assertEqual(entry["version"], self.claude["version"])

        agents_mp = load(os.path.join(ROOT, ".agents", "plugins", "marketplace.json"))
        entry = agents_mp["plugins"][0]
        self.assertEqual(entry["name"], self.codex["name"])
        self.assertEqual(entry["source"], {"source": "local", "path": "./"})

    def test_codex_skills_path_holds_the_skill(self):
        skills = os.path.normpath(os.path.join(ROOT, self.codex["skills"]))
        self.assertTrue(os.path.isfile(os.path.join(skills, self.codex["name"], "SKILL.md")))


class Repository(unittest.TestCase):

    def test_scripts_parse_as_python_3_8(self):
        # README promises Python 3.8+; CI also runs the suite on 3.8 itself
        for path in glob.glob(os.path.join(SCRIPTS, "*.py")):
            with self.subTest(script=os.path.basename(path)), open(path, encoding="utf-8") as f:
                ast.parse(f.read(), feature_version=(3, 8))

    def test_relative_markdown_links_resolve(self):
        link = re.compile(r"\]\(([^)\s]+)\)")
        for md in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
            with open(md, encoding="utf-8") as f:
                targets = link.findall(f.read())
            for target in targets:
                target = target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:") or "<" in target:
                    continue
                with self.subTest(file=rel(md), link=target):
                    self.assertTrue(os.path.exists(os.path.join(os.path.dirname(md), target)))


if __name__ == "__main__":
    unittest.main()
