#!/usr/bin/env python3
"""
self_check.py — sanity checks for a diagram spec + its rendered SVG.

Usage:
    python3 self_check.py spec.json [rendered.svg]

Exits non-zero and prints findings if something is likely wrong. It checks
the spec (dangling references, too many focal elements, diagrams too small
to be worth drawing) and then the actual geometry the renderer produces:
edges that run through a box or on top of each other, edge labels that
overlap a box, another label or another edge, text that does not fit its
box, and groups that swallow nodes they do not contain.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_diagram as rd  # noqa: E402


def check_spec(spec):
    problems = []
    kind = spec.get("kind")
    if kind not in ("boxes", "layers", "sequence"):
        problems.append(f"unknown or missing 'kind': {kind!r}")
        return problems

    def count_focal(items, key="kind"):
        return sum(1 for i in items if i.get(key) == "focal")

    if kind == "boxes":
        nodes = spec.get("nodes", [])
        ids = {n["id"] for n in nodes if "id" in n}
        if len(nodes) < 3:
            problems.append(
                f"only {len(nodes)} node(s) — consider a sentence instead of a diagram"
            )
        for n in nodes:
            if "id" not in n:
                problems.append(f"node {n.get('label')!r} is missing an id")
            if "col" not in n or "row" not in n:
                problems.append(f"node {n.get('id')!r} is missing col/row")
        for e in spec.get("edges", []):
            if e.get("from") not in ids:
                problems.append(f"edge references unknown 'from': {e.get('from')!r}")
            if e.get("to") not in ids:
                problems.append(f"edge references unknown 'to': {e.get('to')!r}")
        focal = count_focal(nodes)
        if focal > 2:
            problems.append(f"{focal} focal nodes — keep it to 1-2 to stay 'one accent'")
        for g in spec.get("groups", []):
            missing = [nid for nid in g.get("nodes", []) if nid not in ids]
            if missing:
                problems.append(f"group {g.get('id')!r} references unknown nodes: {missing}")

    elif kind == "layers":
        layers = spec.get("layers", [])
        if len(layers) < 2:
            problems.append("fewer than 2 layers — a layer diagram needs at least 2")
        focal = count_focal(layers)
        if focal > 2:
            problems.append(f"{focal} focal layers — keep it to 1-2")

    elif kind == "sequence":
        lanes = spec.get("lanes", [])
        lane_ids = {l["id"] for l in lanes if "id" in l}
        messages = spec.get("messages", [])
        if len(lanes) < 2:
            problems.append("fewer than 2 lanes — a sequence needs at least 2 participants")
        if len(messages) < 2:
            problems.append("fewer than 2 messages — consider a sentence instead")
        for m in messages:
            if m.get("from") not in lane_ids:
                problems.append(f"message references unknown lane 'from': {m.get('from')!r}")
            if m.get("to") not in lane_ids:
                problems.append(f"message references unknown lane 'to': {m.get('to')!r}")

    return problems


def check_boxes_geometry(spec):
    problems = []
    lay = rd.layout_boxes(spec)
    boxes, edges, groups = lay["boxes"], lay["edges"], lay["groups"]
    nodes = {n["id"]: n for n in spec["nodes"]}

    ids = list(boxes)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if rd.rects_overlap(boxes[a], boxes[b]):
                problems.append(f"nodes {a!r} and {b!r} overlap — give them different col/row")

    for nid, (x, y, w, h) in boxes.items():
        n = nodes[nid]
        if rd.sans_width(n.get("label", nid), 13) > w - 16:
            problems.append(f"label of node {nid!r} is wider than its box — shorten it")
        if n.get("sublabel") and rd.mono_width(n["sublabel"], 10.5) > w - 16:
            problems.append(f"sublabel of node {nid!r} is wider than its box — shorten it")

    def name(e):
        return f"{e['from']}->{e['to']}"

    for e in edges:
        segs = rd.segments(e["points"])
        for nid, r in boxes.items():
            if nid not in (e["from"], e["to"]) and any(
                    rd.segment_hits_rect(a, b, r) for a, b in segs):
                problems.append(f"edge {name(e)} runs through node {nid!r}")
        for g in groups:
            if g["label"] and any(rd.segment_hits_rect(a, b, g["label_rect"]) for a, b in segs):
                problems.append(f"edge {name(e)} crosses the label of group {g['id']!r}")

    for i, e in enumerate(edges):
        for f in edges[i + 1:]:
            if any(_collinear_overlap(s, t) for s in rd.segments(e["points"])
                   for t in rd.segments(f["points"])):
                problems.append(f"edges {name(e)} and {name(f)} run on top of each other")

    tips = [(e, rd.arrow_tip_rect(e["points"][-1])) for e in edges
            if e["spec"].get("dir", "forward") != "none"]
    labelled = [e for e in edges if e["label_rect"]]
    for i, e in enumerate(labelled):
        r = e["label_rect"]
        what = f"label {e['spec']['label']!r} of edge {name(e)}"
        for nid, b in boxes.items():
            if rd.rects_overlap(r, b):
                problems.append(f"{what} overlaps node {nid!r} — shorten it or widen the grid")
        for f in labelled[i + 1:]:
            if rd.rects_overlap(r, f["label_rect"]):
                problems.append(f"{what} overlaps the label of edge {name(f)}")
        for g in groups:
            if g["label"] and rd.rects_overlap(r, g["label_rect"]):
                problems.append(f"{what} overlaps the label of group {g['id']!r}")
        for f in edges:
            segs = rd.segments(f["points"])
            if f is e:
                segs = [s for j, s in enumerate(segs) if j != e["label_seg"]]
            if any(rd.segment_hits_rect(a, b, r) for a, b in segs):
                problems.append(f"{what} sits on top of edge {name(f)}")
        for f, tip in tips:
            if rd.rects_overlap(r, tip):
                problems.append(f"{what} covers the arrowhead of edge {name(f)}")

    for i, g in enumerate(groups):
        for nid, b in boxes.items():
            if nid not in g["nodes"] and rd.rects_overlap(g["rect"], b):
                problems.append(
                    f"group {g['id']!r} overlaps node {nid!r}, which is not a member — "
                    "move the node out of the group's rows/columns"
                )
        for h in groups[i + 1:]:
            if g["label"] and h["label"] and rd.rects_overlap(g["label_rect"], h["label_rect"]):
                problems.append(f"labels of groups {g['id']!r} and {h['id']!r} overlap")

    return problems


def _collinear_overlap(s, t):
    (a, b), (c, d) = s, t
    if a[1] == b[1] == c[1] == d[1]:
        lo, hi = max(min(a[0], b[0]), min(c[0], d[0])), min(max(a[0], b[0]), max(c[0], d[0]))
        return hi > lo
    if a[0] == b[0] == c[0] == d[0]:
        lo, hi = max(min(a[1], b[1]), min(c[1], d[1])), min(max(a[1], b[1]), max(c[1], d[1]))
        return hi > lo
    return False


def check_layers_geometry(spec):
    problems = []
    for layer in spec.get("layers", []):
        items = " · ".join(layer.get("items", []))
        if rd.mono_width(items, 10.5) > rd.LAYERS_W - 48:
            problems.append(f"items of layer {layer.get('label')!r} are wider than the layer — "
                            "use fewer or shorter keywords")
    return problems


def check_sequence_geometry(spec):
    problems = []
    for lane in spec.get("lanes", []):
        if rd.sans_width(lane.get("label", ""), 12) > rd.LANE_W - 16:
            problems.append(f"label of lane {lane.get('id')!r} is wider than its header box")
    geo = rd.layout_sequence(spec)
    xs = sorted(geo["lane_x"].values())
    for i, r in enumerate(geo["rows"], 1):
        lab = r["label"]
        if not lab:
            continue
        if r["x1"] == r["x2"]:
            right = [x for x in xs if x > r["x1"]]
            if right and lab[0] + lab[2] > right[0] - 8:
                problems.append(f"message {i} ({r['text']!r}) runs into the next lane — shorten it")
            continue
        lo, hi = r["gap"]
        if lab[2] > hi - lo - 8:
            problems.append(
                f"message {i} ({r['text']!r}) is wider than the gap between two lanes — shorten it"
            )
    return problems


def can_lay_out(spec, problems):
    """Geometry checks need a structurally valid, non-empty spec."""
    items = {"boxes": "nodes", "layers": "layers", "sequence": "lanes"}.get(spec.get("kind"))
    return bool(items and spec.get(items)) and not any(
        ("unknown" in p or "missing" in p) for p in problems)


GEOMETRY_CHECKS = {
    "boxes": check_boxes_geometry,
    "layers": check_layers_geometry,
    "sequence": check_sequence_geometry,
}


def check_svg(svg_text):
    problems = []
    if "<svg" not in svg_text:
        problems.append("output does not contain an <svg> element")
    if not re.search(r"<title[ >]", svg_text):
        problems.append("missing accessible <title> (screen readers need it)")
    if "box-shadow" in svg_text or "drop-shadow" in svg_text:
        problems.append("found a shadow — the style guide forbids shadows")
    # ignore the standard SVG/XML namespace declarations, which are always
    # w3.org URLs and are not network requests
    stripped = re.sub(r"https?://www\.w3\.org/\S*", "", svg_text)
    if re.search(r"https?://", stripped):
        problems.append(
            "found an external URL inside the SVG — diagrams must stay self-contained"
        )
    return problems


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)

    spec_path = sys.argv[1]
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    problems = check_spec(spec)
    if can_lay_out(spec, problems):
        problems += GEOMETRY_CHECKS[spec["kind"]](spec)

    if len(sys.argv) > 2:
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            problems += check_svg(f.read())

    if problems:
        print(f"FAIL — {len(problems)} issue(s) in {spec_path}:")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)

    print(f"OK — {spec_path}")


if __name__ == "__main__":
    main()
