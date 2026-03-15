# logic/__init__.py — GraphIt core logic
# Copyright (C) 2025 Kushal Kant Bind
#
# Pure Python — no GTK imports here.
# activity.py calls into this module for all data and math.
# This separation keeps the logic independently testable.

# ── Grid constants ────────────────────────────────────────────────────────────

GRID_CELLS = 10        # grid runs from -GRID_CELLS to +GRID_CELLS
MIN_STEP_PX = 30       # minimum pixels per grid cell (prevents tiny cells)


# ── Challenge definitions ─────────────────────────────────────────────────────
# Each challenge:
#   name        — display title
#   description — one-line task description shown to student
#   hint        — coordinate hint shown below description
#   points      — list of (x, y) target coordinates (empty = free draw)
#   fact        — fun math fact shown after task loads

CHALLENGES = {
    "Triangles": [
        {
            "name": "Right Triangle",
            "description": "Plot 3 points to form a right-angled triangle.",
            "hint": "One angle must be exactly 90°. Try corners at (0,0), (4,0), (0,3)",
            "points": [(0, 0), (4, 0), (0, 3), (0, 0)],
            "fact": "A right triangle has one 90° angle. Used in Pythagoras theorem: a²+b²=c²",
        },
        {
            "name": "Isosceles Triangle",
            "description": "Plot a triangle where two sides are equal length.",
            "hint": "Make it symmetric! Try (0,5), (-3,0), (3,0)",
            "points": [(0, 5), (-3, 0), (3, 0), (0, 5)],
            "fact": "Isosceles triangles have two equal sides and two equal base angles.",
        },
        {
            "name": "Equilateral Triangle",
            "description": "Plot a triangle where all three sides are equal!",
            "hint": "All sides equal, all angles 60°. Try (0,4), (-3,-2), (3,-2)",
            "points": [(0, 4), (-3, -2), (3, -2), (0, 4)],
            "fact": "All sides equal, all angles are 60°. The most symmetric triangle!",
        },
        {
            "name": "Scalene Triangle",
            "description": "Plot a triangle where all three sides are different lengths.",
            "hint": "Try (0,5), (-4,-2), (2,-3) — all sides different!",
            "points": [(0, 5), (-4, -2), (2, -3), (0, 5)],
            "fact": "A scalene triangle has no equal sides and no equal angles.",
        },
    ],
    "Quadrilaterals": [
        {
            "name": "Square",
            "description": "Plot 4 points to make a perfect square.",
            "hint": "All sides equal, all angles 90°. Try (-3,-3), (3,-3), (3,3), (-3,3)",
            "points": [(-3, -3), (3, -3), (3, 3), (-3, 3), (-3, -3)],
            "fact": "A square has 4 equal sides and 4 right angles.",
        },
        {
            "name": "Rectangle",
            "description": "Plot a rectangle — opposite sides equal, all angles 90°.",
            "hint": "Try (-5,-2), (5,-2), (5,2), (-5,2)",
            "points": [(-5, -2), (5, -2), (5, 2), (-5, 2), (-5, -2)],
            "fact": "A rectangle has 4 right angles but sides can have different lengths.",
        },
        {
            "name": "Parallelogram",
            "description": "Plot a shape where opposite sides are parallel.",
            "hint": "Shift the top row: (-3,-2), (3,-2), (5,2), (-1,2)",
            "points": [(-3, -2), (3, -2), (5, 2), (-1, 2), (-3, -2)],
            "fact": "A parallelogram has 2 pairs of parallel sides. Opposite angles are equal.",
        },
        {
            "name": "Rhombus",
            "description": "A diamond shape — all 4 sides equal!",
            "hint": "Try (0,4), (3,0), (0,-4), (-3,0)",
            "points": [(0, 4), (3, 0), (0, -4), (-3, 0), (0, 4)],
            "fact": "A rhombus is like a squished square — all sides equal but angles vary.",
        },
    ],
    "Stars & Polygons": [
        {
            "name": "5-Point Star",
            "description": "Draw a classic 5-pointed star!",
            "hint": "Connect outer and inner points alternately around the center.",
            "points": [
                (0, 5), (1, 2), (4, 2), (2, 0), (3, -3),
                (0, -1), (-3, -3), (-2, 0), (-4, 2), (-1, 2), (0, 5),
            ],
            "fact": "Stars appear in flags of over 35 countries!",
        },
        {
            "name": "Regular Pentagon",
            "description": "Plot a 5-sided polygon with equal sides.",
            "hint": "5 points evenly spaced in a circle. Use the ghost as guide!",
            "points": [
                (0, 5), (5, 2), (3, -4), (-3, -4), (-5, 2), (0, 5),
            ],
            "fact": "A regular pentagon has interior angles of 108° each.",
        },
        {
            "name": "Hexagon",
            "description": "Plot a 6-sided regular hexagon.",
            "hint": "Think of a honeycomb cell: (0,4),(3,2),(3,-2),(0,-4),(-3,-2),(-3,2)",
            "points": [
                (0, 4), (3, 2), (3, -2), (0, -4), (-3, -2), (-3, 2), (0, 4),
            ],
            "fact": "Hexagons are the most efficient shape for tiling — used by bees in honeycombs!",
        },
    ],
    "Free Draw": [
        {
            "name": "Free Draw",
            "description": "No task — plot any points you like and create your own shape!",
            "hint": "Your imagination is the limit. Try making your name with dots!",
            "points": [],
            "fact": "",
        },
    ],
}


# ── Coordinate math ───────────────────────────────────────────────────────────

def compute_step(canvas_w, canvas_h, cells=GRID_CELLS, min_px=MIN_STEP_PX):
    """
    Return the pixel size of one grid cell.

    Fills ~88 % of the shorter canvas axis, but never smaller than min_px.
    Called every draw cycle because the canvas can be resized.

    Args:
        canvas_w: canvas width  in pixels
        canvas_h: canvas height in pixels
        cells:    half the grid range (grid goes -cells … +cells)
        min_px:   floor on cell size so cells stay visible on small screens

    Returns:
        float — pixels per grid unit
    """
    return max(min_px, min(canvas_w, canvas_h) * 0.88 / (cells * 2))


def grid_to_screen(gx, gy, cx, cy, step):
    """
    Convert graph coordinates (gx, gy) to canvas pixel coordinates.

    Mapping:
        screen_x = cx + gx * step
        screen_y = cy - gy * step   ← minus because screen Y grows downward

    Args:
        gx, gy: integer graph coordinates
        cx, cy: pixel position of the graph origin (center of canvas)
        step:   pixels per grid unit

    Returns:
        (sx, sy) tuple of floats
    """
    sx = cx + gx * step
    sy = cy - gy * step
    return sx, sy


def screen_to_grid(sx, sy, cx, cy, step, cells=GRID_CELLS):
    """
    Convert canvas pixel coordinates to the nearest integer grid coordinates,
    clamped to [-cells, +cells] on both axes.

    Args:
        sx, sy: pixel coordinates (e.g. from a mouse event)
        cx, cy: pixel position of the graph origin
        step:   pixels per grid unit
        cells:  grid boundary (clamp target)

    Returns:
        (gx, gy) tuple of ints
    """
    gx = round((sx - cx) / step)
    gy = round(-(sy - cy) / step)
    gx = max(-cells, min(cells, gx))
    gy = max(-cells, min(cells, gy))
    return int(gx), int(gy)


def validate_coord(x, y, cells=GRID_CELLS):
    """
    Check that (x, y) are integers within the grid range.

    Args:
        x, y:  values to validate (can be float from user text entry)
        cells: grid boundary

    Returns:
        (ok: bool, reason: str)
        ok     — True if valid
        reason — human-readable error message, or "" if ok
    """
    try:
        xi, yi = int(x), int(y)
    except (ValueError, TypeError):
        return False, "Please enter whole numbers only"
    if abs(xi) > cells or abs(yi) > cells:
        return False, f"Values must be between -{cells} and {cells}"
    if xi != x or yi != y:
        return False, "Please enter whole numbers only"
    return True, ""


# ── Point history ─────────────────────────────────────────────────────────────

class PointHistory:
    """
    Manages the ordered list of plotted points.

    Keeps GTK out of the data layer — activity.py calls methods here
    and then refreshes the UI separately.

    Usage:
        ph = PointHistory()
        ph.add(3, -2)
        ph.undo()
        ph.clear()
        list(ph)          # iterate over (x, y) tuples
        len(ph)           # number of points
    """

    def __init__(self):
        self._points = []   # list of (int, int) tuples

    # ── mutation ──────────────────────────────────────────────────────────────

    def add(self, x, y):
        """Append a point. x and y are rounded to nearest integer."""
        self._points.append((int(round(x)), int(round(y))))

    def undo(self):
        """Remove the most recently added point. No-op if empty."""
        if self._points:
            self._points.pop()

    def clear(self):
        """Remove all points."""
        self._points = []

    def load(self, points):
        """
        Replace current points with a list of (x, y) pairs.
        Used when restoring from the Sugar journal.
        """
        self._points = [tuple(p) for p in points]

    # ── queries ───────────────────────────────────────────────────────────────

    def as_list(self):
        """Return a copy of the point list (safe for serialisation)."""
        return list(self._points)

    def __len__(self):
        return len(self._points)

    def __iter__(self):
        return iter(self._points)

    def __getitem__(self, idx):
        return self._points[idx]


# ── Completion checking ───────────────────────────────────────────────────────

def check_completion(point_history, challenge):
    """
    Compare plotted points against a challenge's target points.

    Args:
        point_history: PointHistory instance (or any iterable of (x,y))
        challenge:     dict with a "points" key (list of target coords)

    Returns:
        (matched: int, total: int)
        matched — how many unique target points have been plotted
        total   — how many unique target points the challenge requires

    Notes:
        Uses set intersection so duplicate plots don't inflate the count.
        The closing point of a closed shape (same as first) is included in
        the target set, so students must plot it to complete the challenge.
    """
    if not challenge or not challenge.get("points"):
        return 0, 0

    target  = set(map(tuple, challenge["points"]))
    plotted = set(map(tuple, point_history))
    matched = len(plotted & target)
    total   = len(target)
    return matched, total