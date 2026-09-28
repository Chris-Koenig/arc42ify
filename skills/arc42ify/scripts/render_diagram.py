#!/usr/bin/env python3
"""
render_diagram.py — self-contained editorial SVG renderer for arc42 diagrams.

No external dependencies (stdlib only), no network, no Graphviz binary
required. Works identically inside any agent sandbox or a plain CI runner.

Usage:
    python3 render_diagram.py spec.json diagram.svg

Spec format: see references/diagram-spec.md in this skill, or the examples
in assets/templates/*.json.

Design system (see references/style-guide.md for the full rationale):
  - one accent color, used only for the 1-2 focal nodes/edges
  - 1px hairline borders, no shadows, border-radius <= 10
  - all coordinates on a 4px grid
  - three type roles: title (serif/system-serif), label (sans), sublabel (mono)

"boxes" layout: nodes sit on the explicit col/row grid from the spec. Edges
are routed orthogonally around every box (Dijkstra on a 12px lattice with
penalties for bends, crossings and shared segments), every edge gets its own
port on the box side, and each label goes onto a segment where it collides
with nothing. layout_boxes() exposes that geometry so self_check.py can
verify it instead of guessing.
"""
import heapq
import html
import json
import math
import os
import sys

GRID = 4

# ---- default design tokens (overridden by spec["theme"] or a style-guide) ----
DEFAULT_THEME = {
    "paper": "#f7f6f3",
    "ink": "#1a1a1a",
    "muted": "#6b6b6b",
    "paper2": "#ffffff",
    "accent": "#d9622b",
    "hairline": "#d8d5cf",
    "external": "#e7e5e0",
    "font_title": "'Iowan Old Style','Palatino Linotype',Georgia,serif",
    "font_label": "-apple-system,'Segoe UI',Inter,Roboto,sans-serif",
    "font_mono": "'SFMono-Regular','Cascadia Mono','Consolas',monospace",
}

# Outer canvas margin on every side; the title is aligned to it.
MARGIN = 40

# ---- "boxes" geometry. Everything is a multiple of STEP (the routing lattice)
# and node sizes are multiples of PORT_PITCH, so box sides, side centers and
# ports all sit on lattice points.
STEP = 12
PORT_PITCH = 2 * STEP        # distance between neighbouring ports on a side
NODE_W = 192
NODE_H = 72
CELL_W = NODE_W + 168        # column gap fits a ~20-char label between neighbours
CELL_H = NODE_H + 72         # row gap fits a label with clearance above/below
GROUP_PAD = 16
GROUP_PAD_TOP = 32           # room for the group label
LABEL_H = 16
LABEL_CLEAR = 4              # min gap between an edge label and a box/label

# Routing costs (in px of path length). A bend costs as much as 6 lattice
# steps, so the router takes a short detour before it adds a corner.
BEND_COST = 6 * STEP
CROSS_COST = 5 * STEP
JUNCTION_COST = 50 * STEP    # turning on top of another edge
OVERLAP_COST = 100 * STEP    # running along another edge
NEAR_LABEL_COST = 20 * STEP  # running through a placed label
PORT_OFFSET_COST = 1.25      # per px a port sits away from its side's center
TRACK_COST = 0.02            # per px away from a gap/box center line, per step

DIRS = ((1, 0), (0, 1), (-1, 0), (0, -1))  # right, down, left, up

LAYERS_W = 820
LAYER_PITCH = 84

LANE_W = 144
LANE_PITCH = 200
LANE_HEAD = 32
MSG_ROW = 48
SELF_LOOP_W = 36
SELF_LOOP_H = 16


def snap(v):
    return round(v / GRID) * GRID


def ceil_to(v, m):
    return int(math.ceil(v / m) * m)


def esc(s):
    return html.escape(str(s), quote=True)


def merge_theme(spec):
    t = dict(DEFAULT_THEME)
    t.update(spec.get("theme", {}))
    return t


# ---- text metrics (estimates; system fonts differ slightly) -----------------

def mono_width(s, size, tracking=0.0):
    """Advance width of a monospace string: glyphs are ~0.6em wide."""
    return len(str(s)) * size * (0.6 + tracking)


def sans_width(s, size):
    """Rough advance width of a semibold sans string."""
    return len(str(s)) * size * 0.6


def title_width(s):
    return len(str(s)) * 19 * 0.5


def edge_label_size(text):
    # width is a multiple of 8 so that a centered label stays on the 4px grid
    return ceil_to(mono_width(text, 10.5) + 12, 2 * GRID), LABEL_H


# ---- geometry helpers (shared with self_check.py) ---------------------------

def rects_overlap(a, b, clear=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (ax < bx + bw + clear and bx < ax + aw + clear
            and ay < by + bh + clear and by < ay + ah + clear)


def segment_hits_rect(p, q, r, clear=0):
    """True if the axis-parallel segment p-q enters rect r grown by `clear`.
    Merely touching the rect's border does not count."""
    x, y, w, h = r[0] - clear, r[1] - clear, r[2] + 2 * clear, r[3] + 2 * clear
    x0, x1 = sorted((p[0], q[0]))
    y0, y1 = sorted((p[1], q[1]))
    if y0 == y1:  # horizontal
        return y < y0 < y + h and x0 < x + w and x1 > x
    return x < x0 < x + w and y0 < y + h and y1 > y


def segments(points):
    return list(zip(points, points[1:]))


def arrow_tip_rect(p):
    """Area around an edge endpoint that the arrowhead occupies."""
    return (p[0] - 10, p[1] - 10, 20, 20)


def simplify(points):
    """Drop collinear middle points from an orthogonal polyline."""
    out = [points[0]]
    for i in range(1, len(points) - 1):
        a, b, c = out[-1], points[i], points[i + 1]
        if (a[0] == b[0] == c[0]) or (a[1] == b[1] == c[1]):
            continue
        out.append(b)
    out.append(points[-1])
    return out


# ---- "boxes": layout ---------------------------------------------------------

def node_rect(n):
    w = max(2 * PORT_PITCH, round(n.get("w", NODE_W) / PORT_PITCH) * PORT_PITCH)
    h = max(2 * PORT_PITCH, round(n.get("h", NODE_H) / PORT_PITCH) * PORT_PITCH)
    return (n["col"] * CELL_W, n["row"] * CELL_H, w, h)


def group_geometry(g, boxes):
    members = [boxes[i] for i in g.get("nodes", []) if i in boxes]
    if not members:
        return None
    x0 = min(b[0] for b in members) - GROUP_PAD
    y0 = min(b[1] for b in members) - GROUP_PAD_TOP
    x1 = max(b[0] + b[2] for b in members) + GROUP_PAD
    y1 = max(b[1] + b[3] for b in members) + GROUP_PAD
    label = str(g.get("label", "")).upper()
    label_rect = (x0 + 12, y0 + 8, ceil_to(mono_width(label, 10, 0.06), GRID), 12)
    return {
        "id": g.get("id"),
        "rect": (x0, y0, x1 - x0, y1 - y0),
        "label": label,
        "label_rect": label_rect,
        "nodes": [i for i in g.get("nodes", []) if i in boxes],
    }


class Router:
    """Orthogonal edge router on a STEP-spaced lattice.

    Boxes plus one STEP around them are blocked, so edges keep 2 * STEP of
    clearance from every box (and stay clear of group borders, which sit
    GROUP_PAD outside their members). Each edge leaves and enters through its
    own port on a box side. Dijkstra over (point, heading) minimises path
    length plus penalties for bends, off-center ports, crossing or sharing
    other edges and running through placed labels.
    """

    def __init__(self, boxes, soft_rects=()):
        self.boxes = boxes
        self.blocked = set()
        for x, y, w, h in boxes.values():
            for px in range(x - STEP, x + w + STEP + 1, STEP):
                for py in range(y - STEP, y + h + STEP + 1, STEP):
                    self.blocked.add((px, py))
        pad = 4 * STEP
        self.xmin = min(b[0] for b in boxes.values()) - pad
        self.xmax = max(b[0] + b[2] for b in boxes.values()) + pad
        self.ymin = min(b[1] for b in boxes.values()) - pad
        self.ymax = max(b[1] + b[3] for b in boxes.values()) + pad

        # Among equally short routes, prefer running down the middle of a gap
        # or along a box's center line.
        cols = [b[0] // CELL_W for b in boxes.values()]
        rows = [b[1] // CELL_H for b in boxes.values()]
        gap_x = (CELL_W - NODE_W) // 2
        gap_y = (CELL_H - NODE_H) // 2
        pref_x = [c * CELL_W - gap_x for c in range(min(cols), max(cols) + 2)]
        pref_x += [b[0] + b[2] // 2 for b in boxes.values()]
        pref_y = [r * CELL_H - gap_y for r in range(min(rows), max(rows) + 2)]
        pref_y += [b[1] + b[3] // 2 for b in boxes.values()]
        self.xpen = {x: TRACK_COST * min(abs(x - p) for p in pref_x)
                     for x in range(self.xmin, self.xmax + 1, STEP)}
        self.ypen = {y: TRACK_COST * min(abs(y - p) for p in pref_y)
                     for y in range(self.ymin, self.ymax + 1, STEP)}

        self.used_edges = set()
        self.used_points = set()
        self.used_ports = set()
        self.soft = {}
        for r in soft_rects:
            self.add_soft(r)

    def add_soft(self, rect):
        x, y, w, h = rect
        d = STEP // 2
        for px in range(ceil_to(x - d, STEP), x + w + d + 1, STEP):
            for py in range(ceil_to(y - d, STEP), y + h + d + 1, STEP):
                self.soft[(px, py)] = self.soft.get((px, py), 0) + NEAR_LABEL_COST

    def ports(self, node_id):
        """Free ports of a box: (point on side, first unblocked lattice point
        straight out from it, outward heading, penalty)."""
        x, y, w, h = self.boxes[node_id]
        out = []
        for d, (dx, dy) in enumerate(DIRS):
            length = h if dx else w
            center = length // 2
            k_max = center // PORT_PITCH
            for k in range(-k_max, k_max + 1):
                o = center + k * PORT_PITCH
                if not STEP <= o <= length - STEP:
                    continue
                if dx:
                    p0 = (x + w if dx > 0 else x, y + o)
                else:
                    p0 = (x + o, y + h if dy > 0 else y)
                p1 = (p0[0] + 2 * dx * STEP, p0[1] + 2 * dy * STEP)
                if p0 in self.used_ports or p1 in self.blocked:
                    continue
                out.append((p0, p1, d, PORT_OFFSET_COST * abs(o - center)))
        return out

    def _step_cost(self, p, q, d, nd):
        c = STEP
        if nd != d:
            c += BEND_COST
            if p in self.used_points:
                c += JUNCTION_COST
        c += self.xpen.get(q[0], 0) if DIRS[nd][0] == 0 else self.ypen.get(q[1], 0)
        if (min(p, q), max(p, q)) in self.used_edges:
            c += OVERLAP_COST
        elif q in self.used_points:
            c += CROSS_COST
        return c + self.soft.get(q, 0)

    def route(self, src, dst):
        heap, best, prev = [], {}, {}
        tie = 0

        def push(key, cost, parent):
            nonlocal tie
            if cost < best.get(key, math.inf):
                best[key] = cost
                prev[key] = parent
                tie += 1
                heapq.heappush(heap, (cost, tie, key))

        for p0, p1, d, pen in self.ports(src):
            push((p1, d), self._step_cost(p0, p1, d, d) + pen, ("start", p0))
        goals = {}
        for q0, q1, d, pen in self.ports(dst):
            goals.setdefault(q1, []).append((q0, (d + 2) % 4, pen))

        while heap:
            cost, _, key = heapq.heappop(heap)
            if cost > best[key]:
                continue
            if key[0] == "goal":
                return self._commit(self._path(prev, key))
            p, d = key
            for q0, inward, pen in goals.get(p, ()):
                if inward != (d + 2) % 4:  # no U-turn into the port
                    push(("goal", q0), cost + self._step_cost(p, q0, d, inward) + pen, key)
            for nd, (dx, dy) in enumerate(DIRS):
                if nd == (d + 2) % 4:
                    continue
                q = (p[0] + dx * STEP, p[1] + dy * STEP)
                if (q in self.blocked or not self.xmin <= q[0] <= self.xmax
                        or not self.ymin <= q[1] <= self.ymax):
                    continue
                push((q, nd), cost + self._step_cost(p, q, d, nd), key)
        raise SystemExit(f"could not route edge {src} -> {dst}: no free port left")

    @staticmethod
    def _path(prev, goal_key):
        pts = [goal_key[1]]
        key = prev[goal_key]
        while True:
            pts.append(key[0])
            parent = prev[key]
            if parent[0] == "start":
                pts.append(parent[1])
                break
            key = parent
        pts.reverse()
        return pts

    def _commit(self, pts):
        self.used_ports.update((pts[0], pts[-1]))
        for p, q in zip(pts, pts[1:]):
            self.used_edges.add((min(p, q), max(p, q)))
            self.used_points.update((p, q))
        return simplify(pts)


def _is_direct(e, boxes):
    """Same row/column with nothing in between: a straight line will do."""
    a, b = boxes[e["from"]], boxes[e["to"]]
    ca = (a[0] + a[2] // 2, a[1] + a[3] // 2)
    cb = (b[0] + b[2] // 2, b[1] + b[3] // 2)
    if ca[0] != cb[0] and ca[1] != cb[1]:
        return False
    return not any(segment_hits_rect(ca, cb, r)
                   for k, r in boxes.items() if k not in (e["from"], e["to"]))


def _center_distance(e, boxes):
    a, b = boxes[e["from"]], boxes[e["to"]]
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def place_label(text, pts, boxes, taken, lines, tips):
    """Put the label on the longest segment where it hits nothing; try the
    midpoint first, then slide toward the ends, then shorter segments."""
    w, h = edge_label_size(text)
    segs = segments(pts)
    order = sorted(range(len(segs)),
                   key=lambda i: -(abs(segs[i][1][0] - segs[i][0][0])
                                   + abs(segs[i][1][1] - segs[i][0][1])))
    candidates = []
    for i in order:
        (ax, ay), (bx, by) = segs[i]
        for f in (0.5, 0.35, 0.65, 0.2, 0.8):
            cx, cy = snap(ax + (bx - ax) * f), snap(ay + (by - ay) * f)
            candidates.append((i, (cx - w // 2, cy - h // 2, w, h)))

    def free(i, r):
        return not (
            any(rects_overlap(r, b, LABEL_CLEAR) for b in boxes.values())
            or any(rects_overlap(r, t, LABEL_CLEAR) for t in taken)
            or any(rects_overlap(r, t) for t in tips)
            or any(segment_hits_rect(a, b, r, 2) for a, b in lines)
            or any(segment_hits_rect(a, b, r, 2)
                   for j, (a, b) in enumerate(segs) if j != i)
        )

    for i, r in candidates:
        if free(i, r):
            return r, i
    return candidates[0][1], candidates[0][0]


def layout_boxes(spec):
    """Place nodes, route edges, place labels. Returns the geometry that
    render_boxes() draws and self_check.py verifies."""
    boxes = {n["id"]: node_rect(n) for n in spec["nodes"]}
    groups = [g for g in (group_geometry(g, boxes) for g in spec.get("groups", [])) if g]
    group_labels = [g["label_rect"] for g in groups if g["label"]]

    edges = spec.get("edges", [])
    router = Router(boxes, group_labels)
    order = sorted(range(len(edges)),
                   key=lambda i: (not _is_direct(edges[i], boxes),
                                  _center_distance(edges[i], boxes), i))
    routed = [None] * len(edges)
    taken = list(group_labels)
    lines, tips = [], []
    for i in order:
        e = edges[i]
        pts = router.route(e["from"], e["to"])
        if e.get("dir", "forward") != "none":
            tips.append(arrow_tip_rect(pts[-1]))
        label_rect, label_seg = None, None
        if e.get("label"):
            label_rect, label_seg = place_label(e["label"], pts, boxes, taken, lines, tips)
            taken.append(label_rect)
            router.add_soft(label_rect)
        lines.extend(segments(pts))
        routed[i] = {"from": e["from"], "to": e["to"], "spec": e, "points": pts,
                     "label_rect": label_rect, "label_seg": label_seg}

    rects = list(boxes.values()) + [g["rect"] for g in groups]
    rects += [r["label_rect"] for r in routed if r["label_rect"]]
    xs = [r[0] for r in rects] + [r[0] + r[2] for r in rects]
    ys = [r[1] for r in rects] + [r[1] + r[3] for r in rects]
    for r in routed:
        xs += [p[0] for p in r["points"]]
        ys += [p[1] for p in r["points"]]
    return {"boxes": boxes, "groups": groups, "edges": routed,
            "bounds": (min(xs), min(ys), max(xs), max(ys))}


# ---- "boxes": drawing ---------------------------------------------------------

def node_svg(n, rect, theme):
    x, y, w, h = rect
    kind = n.get("kind", "default")
    fill, stroke, stroke_w = theme["paper2"], theme["hairline"], 1
    if kind == "focal":
        fill = theme["accent"] + "1a"  # ~10% alpha suffix on hex works in modern SVG
        stroke = theme["accent"]
        stroke_w = 1.5
    if kind == "external":
        fill = theme["external"]

    parts = [
        f'<g data-node-id="{esc(n["id"])}">',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}"/>',
    ]
    label = n.get("label", n["id"])
    sub = n.get("sublabel")
    ty = y + (h / 2 - 6 if sub else h / 2 + 4)
    parts.append(
        f'<text x="{x + w // 2}" y="{snap(ty)}" text-anchor="middle" '
        f'font-family="{theme["font_label"]}" font-size="13" font-weight="600" '
        f'fill="{theme["ink"]}">{esc(label)}</text>'
    )
    if sub:
        parts.append(
            f'<text x="{x + w // 2}" y="{snap(ty + 18)}" text-anchor="middle" '
            f'font-family="{theme["font_mono"]}" font-size="10.5" '
            f'fill="{theme["muted"]}">{esc(sub)}</text>'
        )
    parts.append("</g>")
    return "".join(parts)


def edge_label_svg(text, rect, theme):
    x, y, w, h = rect
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{theme["paper"]}"/>'
        f'<text x="{x + w // 2}" y="{y + 12}" text-anchor="middle" '
        f'font-family="{theme["font_mono"]}" font-size="10.5" fill="{theme["muted"]}">'
        f"{esc(text)}</text>"
    )


def render_boxes(spec, theme):
    lay = layout_boxes(spec)
    x0, y0, x1, y1 = lay["bounds"]
    body = []

    for g in lay["groups"]:
        gx, gy, gw, gh = g["rect"]
        body.append(
            f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="10" ry="10" '
            f'fill="none" stroke="{theme["hairline"]}" stroke-width="1" stroke-dasharray="2 5"/>'
        )
        body.append(
            f'<text x="{gx + 12}" y="{gy + 18}" font-family="{theme["font_mono"]}" '
            f'font-size="10" letter-spacing="0.06em" fill="{theme["muted"]}">'
            f'{esc(g["label"])}</text>'
        )

    # Paths first, then boxes, then labels: a label is never painted over.
    for r in lay["edges"]:
        e = r["spec"]
        d = "M " + " L ".join(f"{x} {y}" for x, y in r["points"])
        dash = ' stroke-dasharray="4 4"' if e.get("style") == "dashed" else ""
        color = "accent" if e.get("kind") == "focal" else "muted"
        marker = f' marker-end="url(#arrow-{color})"' if e.get("dir", "forward") != "none" else ""
        body.append(f'<path d="{d}" fill="none" stroke="{theme[color]}" '
                    f'stroke-width="1.25"{dash}{marker}/>')

    for n in spec["nodes"]:
        body.append(node_svg(n, lay["boxes"][n["id"]], theme))

    for r in lay["edges"]:
        if r["label_rect"]:
            body.append(edge_label_svg(r["spec"]["label"], r["label_rect"], theme))

    inner = "".join(body)
    return x1 - x0, y1 - y0, f'<g transform="translate({-x0},{-y0})">{inner}</g>'


# ---- "layers" -------------------------------------------------------------------

def render_layers(spec, theme):
    layers = spec["layers"]
    row_h = LAYER_PITCH - 16
    body = []
    for i, layer in enumerate(layers):
        y = i * LAYER_PITCH
        is_focal = layer.get("kind") == "focal"
        fill = theme["accent"] + "14" if is_focal else theme["paper2"]
        stroke = theme["accent"] if is_focal else theme["hairline"]
        body.append(
            f'<rect x="0" y="{y}" width="{LAYERS_W}" height="{row_h}" rx="8" ry="8" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{1.5 if is_focal else 1}"/>'
        )
        body.append(
            f'<text x="24" y="{y + 28}" font-family="{theme["font_label"]}" font-size="13" '
            f'font-weight="700" fill="{theme["ink"]}">{esc(layer["label"])}</text>'
        )
        items = layer.get("items", [])
        if items:
            body.append(
                f'<text x="24" y="{y + 48}" font-family="{theme["font_mono"]}" font-size="10.5" '
                f'fill="{theme["muted"]}">{esc(" · ".join(items))}</text>'
            )
    return LAYERS_W, len(layers) * LAYER_PITCH - 16, "".join(body)


# ---- "sequence" ----------------------------------------------------------------

def layout_sequence(spec):
    """Geometry of a sequence diagram: lane centers, one row per message.

    Shared with self_check.py. A message to its own lane becomes a small
    loop right of the lifeline with its label beside it. A message that
    spans several lanes puts its label in the gap next to the sender, so it
    never hides a lifeline in between. "numbered": true prefixes each label
    with its step number.
    """
    lane_x = {lane["id"]: LANE_W // 2 + i * LANE_PITCH for i, lane in enumerate(spec["lanes"])}
    rows = []
    y = LANE_HEAD + 48
    for i, m in enumerate(spec["messages"]):
        if rows:
            y += MSG_ROW + (SELF_LOOP_H if rows[-1]["x1"] == rows[-1]["x2"] else 0)
        text = m.get("label", "")
        if text and spec.get("numbered"):
            text = f"{i + 1} · {text}"
        x1, x2 = lane_x[m["from"]], lane_x[m["to"]]
        label_rect, gap = None, None
        if text:
            w, h = edge_label_size(text)
            if x1 == x2:
                label_rect = (x1 + SELF_LOOP_W + 4, y, w, h)
            else:
                gap = tuple(sorted((x1, x1 + (LANE_PITCH if x2 > x1 else -LANE_PITCH))))
                label_rect = (snap(sum(gap) / 2 - w / 2), y - 20, w, h)
        rows.append({"message": m, "y": y, "x1": x1, "x2": x2,
                     "text": text, "label": label_rect, "gap": gap})
    return {"lane_x": lane_x, "rows": rows}


def render_sequence(spec, theme):
    geo = layout_sequence(spec)
    lane_x, rows = geo["lane_x"], geo["rows"]
    last = rows[-1] if rows else None
    height = (last["y"] + 32 + (SELF_LOOP_H if last["x1"] == last["x2"] else 0)
              if last else LANE_HEAD + 48)
    width = (len(spec["lanes"]) - 1) * LANE_PITCH + LANE_W
    for r in rows:
        if r["label"]:
            width = max(width, r["label"][0] + r["label"][2])

    body = []
    for lane in spec["lanes"]:
        x = lane_x[lane["id"]]
        body.append(
            f'<rect x="{x - LANE_W // 2}" y="0" width="{LANE_W}" height="{LANE_HEAD}" rx="6" ry="6" '
            f'fill="{theme["paper2"]}" stroke="{theme["hairline"]}"/>'
        )
        body.append(
            f'<text x="{x}" y="21" text-anchor="middle" font-family="{theme["font_label"]}" '
            f'font-size="12" font-weight="600" fill="{theme["ink"]}">{esc(lane["label"])}</text>'
        )
        body.append(
            f'<line x1="{x}" y1="{LANE_HEAD}" x2="{x}" y2="{height}" '
            f'stroke="{theme["hairline"]}" stroke-width="1"/>'
        )

    for r in rows:
        m, y, x1, x2 = r["message"], r["y"], r["x1"], r["x2"]
        dash = ' stroke-dasharray="4 4"' if m.get("dashed") else ""
        color = "accent" if m.get("kind") == "focal" else "ink"
        if x1 == x2:
            d = f"M {x1} {y} H {x1 + SELF_LOOP_W} V {y + SELF_LOOP_H} H {x1}"
        else:
            d = f"M {x1} {y} H {x2}"
        body.append(
            f'<path d="{d}" fill="none" stroke="{theme[color]}" stroke-width="1.25"{dash} '
            f'marker-end="url(#arrow-{color})"/>'
        )
        if r["label"]:
            lx, ly, lw, lh = r["label"]
            tx, anchor = (lx + 6, "start") if x1 == x2 else (lx + lw // 2, "middle")
            body.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="{theme["paper"]}"/>')
            body.append(
                f'<text x="{tx}" y="{ly + 12}" text-anchor="{anchor}" font-family="{theme["font_mono"]}" '
                f'font-size="10.5" fill="{theme["muted"]}">{esc(r["text"])}</text>'
            )
    return width, height, "".join(body)


RENDERERS = {"boxes": render_boxes, "layers": render_layers, "sequence": render_sequence}


def marker_defs(theme):
    # one arrowhead per stroke color, so an accent edge gets an accent head
    return "".join(
        f'<marker id="arrow-{name}" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{theme[name]}"/></marker>'
        for name in ("muted", "accent", "ink")
    )


def render_svg(spec):
    """Renderers draw their content with its top-left corner at (0, 0);
    this adds the title block and an even MARGIN on every side."""
    theme = merge_theme(spec)
    kind = spec.get("kind", "boxes")
    if kind not in RENDERERS:
        raise SystemExit(f"unknown diagram kind: {kind} (expected one of {list(RENDERERS)})")

    content_w, content_h, body = RENDERERS[kind](spec, theme)

    title = spec.get("title", "")
    subtitle = spec.get("subtitle", "")
    header = ""
    content_top = MARGIN
    header_w = 0
    if title:
        content_top = 80 if subtitle else 64
        header_w = title_width(title)
        header = (
            f'<text x="{MARGIN}" y="30" font-family="{theme["font_title"]}" font-size="19" '
            f'font-style="italic" fill="{theme["ink"]}">{esc(title)}</text>'
        )
        if subtitle:
            header_w = max(header_w, mono_width(subtitle.upper(), 10.5, 0.04))
            header += (
                f'<text x="{MARGIN}" y="48" font-family="{theme["font_mono"]}" font-size="10.5" '
                f'letter-spacing="0.04em" fill="{theme["muted"]}">{esc(subtitle.upper())}</text>'
            )

    width = ceil_to(max(content_w, header_w) + 2 * MARGIN, GRID)
    height = ceil_to(content_top + content_h + MARGIN, GRID)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"
     width="{width}" height="{height}" role="img"
     aria-labelledby="dd-title dd-desc">
  <title id="dd-title">{esc(title or "Diagram")}</title>
  <desc id="dd-desc">{esc(subtitle or "arc42 diagram generated by the arc42ify skill")}</desc>
  <defs>{marker_defs(theme)}</defs>
  <rect x="0" y="0" width="{width}" height="{height}" fill="{theme["paper"]}"/>
  {header}
  <g transform="translate({MARGIN},{content_top})">
  {body}
  </g>
</svg>'''


def render(spec_path, out_path):
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    svg = render_svg(spec)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    # LF on every OS, so a re-render is byte-identical on Windows too
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    return out_path


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")  # e.g. a cp1252 console on Windows
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(1)
    out = render(sys.argv[1], sys.argv[2])
    print(f"wrote {out}")
