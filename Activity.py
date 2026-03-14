# GraphIt — Learn coordinates by plotting on a graph
# Copyright (C) 2025 Kushal Kant Bind
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import json
import math
import os
from gettext import gettext as _

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton, StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton


# ── Predefined challenge shapes ──────────────────────────────────────────────

CHALLENGES = [
    {
        "name": _("Star"),
        "description": _("Connect the dots to draw a 5-pointed star!"),
        "points": [
            (0, 4), (1, 1), (4, 1), (2, -1), (3, -4),
            (0, -2), (-3, -4), (-2, -1), (-4, 1), (-1, 1), (0, 4)
        ],
        "hint": _("Start at the top and work your way around!"),
    },
    {
        "name": _("House"),
        "description": _("Plot these points to build a house!"),
        "points": [
            (-3, 0), (3, 0), (3, 4), (0, 7), (-3, 4), (-3, 0),
            (-3, 4), (3, 4),
            (1, 0), (1, 3), (-1, 3), (-1, 0)
        ],
        "hint": _("The roof peak is at (0, 7)"),
    },
    {
        "name": _("Rocket"),
        "description": _("Launch a rocket with coordinates!"),
        "points": [
            (0, 8), (2, 4), (2, -2), (1, -4), (-1, -4), (-2, -2),
            (-2, 4), (0, 8),
            (-2, 2), (-4, 0), (-2, -1),
            (2, 2), (4, 0), (2, -1),
        ],
        "hint": _("Rockets need fins on both sides!"),
    },
    {
        "name": _("Free Draw"),
        "description": _("Plot any points you like — make your own shape!"),
        "points": [],
        "hint": _("Your imagination is the limit!"),
    },
]


class GraphIt(activity.Activity):
    """GraphIt — an interactive coordinate graph learning activity."""

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        # ── Game state ────────────────────────────────────────────────────
        self.plotted_points = []          # [(x, y), ...]
        self.connected_lines = []         # [((x1,y1),(x2,y2)), ...]
        self.current_challenge = None
        self.challenge_index = 0
        self.connect_mode = False         # if True, click connects last point
        self.hover_point = None           # grid snap preview

        # ── UI ────────────────────────────────────────────────────────────
        self._setup_css()
        self._create_toolbar()
        self._create_main_ui()

    # ── CSS ──────────────────────────────────────────────────────────────────

    def _setup_css(self):
        css = b"""
        .sidebar {
            background-color: #1a1a2e;
            border-radius: 0 12px 12px 0;
        }
        .challenge-title {
            font-size: 15pt;
            font-weight: bold;
            color: #e94560;
        }
        .point-row {
            font-family: monospace;
            font-size: 12pt;
            color: #a8dadc;
            padding: 2px 8px;
            border-radius: 4px;
        }
        .point-row:hover {
            background-color: rgba(233,69,96,0.15);
        }
        .hint-label {
            font-size: 10pt;
            color: #ffd166;
            font-style: italic;
        }
        .input-coord {
            font-family: monospace;
            font-size: 13pt;
            background-color: #16213e;
            color: #e0e0e0;
            border-radius: 6px;
        }
        .plot-btn {
            font-size: 12pt;
            font-weight: bold;
            background-color: #e94560;
            color: white;
            border-radius: 8px;
            min-height: 40px;
        }
        .plot-btn:hover {
            background-color: #c73652;
        }
        .success-banner {
            font-size: 16pt;
            font-weight: bold;
            color: #06d6a0;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _create_toolbar(self):
        tb = ToolbarBox()
        self.set_toolbar_box(tb)
        bar = tb.toolbar

        bar.insert(ActivityToolbarButton(self), -1)

        sep = Gtk.SeparatorToolItem()
        sep.props.draw = True
        bar.insert(sep, -1)

        # Clear button
        clear_btn = ToolButton("edit-clear")
        clear_btn.set_tooltip(_("Clear all points"))
        clear_btn.connect("clicked", self._clear_cb)
        bar.insert(clear_btn, -1)

        # Undo button
        undo_btn = ToolButton("edit-undo")
        undo_btn.set_tooltip(_("Undo last point"))
        undo_btn.connect("clicked", self._undo_cb)
        bar.insert(undo_btn, -1)

        sep2 = Gtk.SeparatorToolItem()
        sep2.props.draw = True
        bar.insert(sep2, -1)

        # Connect-dots toggle
        self.connect_toggle = ToggleToolButton("format-justify-fill")
        self.connect_toggle.set_tooltip(_("Connect dots with lines"))
        self.connect_toggle.connect("toggled", self._connect_toggled_cb)
        bar.insert(self.connect_toggle, -1)

        sep3 = Gtk.SeparatorToolItem()
        sep3.props.draw = True
        bar.insert(sep3, -1)

        # Challenge button
        challenge_btn = ToolButton("go-next")
        challenge_btn.set_tooltip(_("Next challenge"))
        challenge_btn.connect("clicked", self._next_challenge_cb)
        bar.insert(challenge_btn, -1)

        # Help button
        help_btn = ToolButton("toolbar-help")
        help_btn.set_tooltip(_("Help"))
        help_btn.connect("clicked", self._help_cb)
        bar.insert(help_btn, -1)

        # Spacer
        spacer = Gtk.SeparatorToolItem()
        spacer.props.draw = False
        spacer.set_expand(True)
        bar.insert(spacer, -1)

        bar.insert(StopButton(self), -1)
        tb.show_all()

    # ── Main UI ───────────────────────────────────────────────────────────────

    def _create_main_ui(self):
        """Horizontal split: graph canvas (left) + sidebar (right)."""
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # ── Canvas ──────────────────────────────────────────────
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.LEAVE_NOTIFY_MASK
        )
        self.canvas.connect("draw", self._draw_cb)
        self.canvas.connect("button-press-event", self._canvas_click_cb)
        self.canvas.connect("motion-notify-event", self._canvas_motion_cb)
        self.canvas.connect("leave-notify-event", self._canvas_leave_cb)
        hbox.pack_start(self.canvas, True, True, 0)

        # ── Sidebar ──────────────────────────────────────────────
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sidebar.set_size_request(240, -1)
        sidebar.set_border_width(14)
        sidebar.get_style_context().add_class("sidebar")

        # Challenge name
        self.challenge_label = Gtk.Label(label=_("Free Draw"))
        self.challenge_label.get_style_context().add_class("challenge-title")
        self.challenge_label.set_line_wrap(True)
        self.challenge_label.set_xalign(0)
        sidebar.pack_start(self.challenge_label, False, False, 0)

        # Challenge description
        self.desc_label = Gtk.Label(label=_("Click the graph to plot points!"))
        self.desc_label.set_line_wrap(True)
        self.desc_label.set_xalign(0)
        self.desc_label.override_color(
            Gtk.StateFlags.NORMAL,
            Gdk.RGBA(0.8, 0.8, 0.8, 1)
        )
        sidebar.pack_start(self.desc_label, False, False, 0)

        # Hint
        self.hint_label = Gtk.Label(label="")
        self.hint_label.get_style_context().add_class("hint-label")
        self.hint_label.set_line_wrap(True)
        self.hint_label.set_xalign(0)
        sidebar.pack_start(self.hint_label, False, False, 0)

        sidebar.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            False, False, 4
        )

        # Manual coordinate entry
        coord_label = Gtk.Label(label=_("Enter a point (x, y):"))
        coord_label.set_xalign(0)
        coord_label.override_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(0.7, 0.7, 0.7, 1)
        )
        sidebar.pack_start(coord_label, False, False, 0)

        coord_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.x_entry = Gtk.Entry()
        self.x_entry.set_placeholder_text("x")
        self.x_entry.set_width_chars(4)
        self.x_entry.get_style_context().add_class("input-coord")
        self.y_entry = Gtk.Entry()
        self.y_entry.set_placeholder_text("y")
        self.y_entry.set_width_chars(4)
        self.y_entry.get_style_context().add_class("input-coord")
        plot_btn = Gtk.Button(label=_("Plot"))
        plot_btn.get_style_context().add_class("plot-btn")
        plot_btn.connect("clicked", self._manual_plot_cb)
        self.x_entry.connect("activate", self._manual_plot_cb)
        self.y_entry.connect("activate", self._manual_plot_cb)
        coord_row.pack_start(self.x_entry, True, True, 0)
        coord_row.pack_start(Gtk.Label(label=","), False, False, 0)
        coord_row.pack_start(self.y_entry, True, True, 0)
        coord_row.pack_start(plot_btn, False, False, 0)
        sidebar.pack_start(coord_row, False, False, 0)

        sidebar.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            False, False, 4
        )

        # Points list
        pts_title = Gtk.Label(label=_("Your Points:"))
        pts_title.set_xalign(0)
        pts_title.override_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(0.6, 0.8, 0.9, 1)
        )
        sidebar.pack_start(pts_title, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        self.points_list = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=2
        )
        scroll.add(self.points_list)
        sidebar.pack_start(scroll, True, True, 0)

        # Success banner (hidden initially)
        self.success_label = Gtk.Label(label="")
        self.success_label.get_style_context().add_class("success-banner")
        self.success_label.set_no_show_all(True)
        sidebar.pack_end(self.success_label, False, False, 0)

        hbox.pack_start(sidebar, False, False, 0)
        self.set_canvas(hbox)
        hbox.show_all()

        # Load first challenge
        self._load_challenge(0)

    # ── Challenge loading ─────────────────────────────────────────────────────

    def _load_challenge(self, index):
        self.challenge_index = index % len(CHALLENGES)
        self.current_challenge = CHALLENGES[self.challenge_index]
        self.plotted_points = []
        self.connected_lines = []
        self._refresh_points_list()
        self.success_label.hide()

        self.challenge_label.set_text(self.current_challenge["name"])
        self.desc_label.set_text(self.current_challenge["description"])
        self.hint_label.set_text(self.current_challenge["hint"])
        self.canvas.queue_draw()

    def _next_challenge_cb(self, btn):
        self._load_challenge(self.challenge_index + 1)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw_cb(self, widget, cr):
        alloc = widget.get_allocation()
        W, H = alloc.width, alloc.height

        # Grid parameters
        grid_size = min(W, H) * 0.85
        cx, cy = W / 2, H / 2
        cells = 10                          # -10 to +10
        step = grid_size / (cells * 2)      # pixels per unit

        # ── Background ──────────────────────────────────────────
        cr.set_source_rgb(0.05, 0.07, 0.14)
        cr.paint()

        # ── Subtle grid lines ────────────────────────────────────
        cr.set_line_width(0.5)
        for i in range(-cells, cells + 1):
            # vertical
            x = cx + i * step
            cr.set_source_rgba(0.3, 0.4, 0.6, 0.3)
            cr.move_to(x, cy - cells * step)
            cr.line_to(x, cy + cells * step)
            cr.stroke()
            # horizontal
            y = cy + i * step
            cr.move_to(cx - cells * step, y)
            cr.line_to(cx + cells * step, y)
            cr.stroke()

        # ── Axes ─────────────────────────────────────────────────
        cr.set_line_width(2)
        cr.set_source_rgba(0.6, 0.7, 0.9, 0.9)
        # X axis
        cr.move_to(cx - cells * step, cy)
        cr.line_to(cx + cells * step, cy)
        cr.stroke()
        # Y axis
        cr.move_to(cx, cy - cells * step)
        cr.line_to(cx, cy + cells * step)
        cr.stroke()

        # ── Axis arrows ──────────────────────────────────────────
        cr.set_source_rgba(0.6, 0.7, 0.9, 0.9)
        ax_end = cx + cells * step
        ay_end = cy - cells * step
        # X arrow
        cr.move_to(ax_end, cy)
        cr.line_to(ax_end - 8, cy - 5)
        cr.line_to(ax_end - 8, cy + 5)
        cr.close_path(); cr.fill()
        # Y arrow
        cr.move_to(cx, ay_end)
        cr.line_to(cx - 5, ay_end + 8)
        cr.line_to(cx + 5, ay_end + 8)
        cr.close_path(); cr.fill()

        # ── Axis labels ───────────────────────────────────────────
        cr.set_source_rgba(0.7, 0.8, 1.0, 0.9)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(13)
        cr.move_to(ax_end + 4, cy + 5)
        cr.show_text("x")
        cr.move_to(cx + 6, ay_end - 4)
        cr.show_text("y")

        # ── Tick labels ───────────────────────────────────────────
        cr.set_font_size(9)
        cr.set_source_rgba(0.5, 0.6, 0.75, 0.7)
        for i in range(-cells, cells + 1):
            if i == 0:
                continue
            # X ticks
            tx = cx + i * step
            cr.move_to(tx, cy + 3)
            cr.line_to(tx, cy - 3)
            cr.stroke()
            if i % 2 == 0:
                label = str(i)
                ext = cr.text_extents(label)
                cr.move_to(tx - ext.width / 2, cy + 14)
                cr.show_text(label)
            # Y ticks
            ty = cy - i * step
            cr.move_to(cx - 3, ty)
            cr.line_to(cx + 3, ty)
            cr.stroke()
            if i % 2 == 0:
                label = str(i)
                ext = cr.text_extents(label)
                cr.move_to(cx - ext.width - 6, ty + ext.height / 2)
                cr.show_text(label)

        def to_screen(x, y):
            return cx + x * step, cy - y * step

        # ── Challenge ghost points ────────────────────────────────
        if self.current_challenge and self.current_challenge["points"]:
            ghost_pts = self.current_challenge["points"]
            cr.set_source_rgba(0.9, 0.4, 0.2, 0.18)
            cr.set_line_width(1.5)
            sx, sy = to_screen(*ghost_pts[0])
            cr.move_to(sx, sy)
            for p in ghost_pts[1:]:
                sx, sy = to_screen(*p)
                cr.line_to(sx, sy)
            cr.stroke()
            # Ghost dots
            for p in ghost_pts:
                sx, sy = to_screen(*p)
                cr.set_source_rgba(0.9, 0.5, 0.2, 0.25)
                cr.arc(sx, sy, 5, 0, 2 * math.pi)
                cr.fill()

        # ── Connected lines (user drawn) ──────────────────────────
        if len(self.plotted_points) >= 2 and self.connect_mode:
            cr.set_line_width(2.5)
            cr.set_source_rgba(0.41, 0.85, 0.63, 0.85)
            sx, sy = to_screen(*self.plotted_points[0])
            cr.move_to(sx, sy)
            for p in self.plotted_points[1:]:
                sx, sy = to_screen(*p)
                cr.line_to(sx, sy)
            cr.stroke()

        # ── Hover snap preview ────────────────────────────────────
        if self.hover_point:
            hx, hy = to_screen(*self.hover_point)
            cr.set_source_rgba(1, 0.84, 0.0, 0.5)
            cr.arc(hx, hy, 7, 0, 2 * math.pi)
            cr.fill()
            cr.set_source_rgba(1, 1, 1, 0.4)
            cr.arc(hx, hy, 7, 0, 2 * math.pi)
            cr.set_line_width(1.5)
            cr.stroke()
            # Coordinate label on hover
            cr.set_font_size(11)
            cr.set_source_rgba(1, 0.84, 0, 0.9)
            cr.move_to(hx + 10, hy - 6)
            cr.show_text(f"({self.hover_point[0]}, {self.hover_point[1]})")

        # ── Plotted points ────────────────────────────────────────
        COLORS = [
            (0.91, 0.27, 0.37),   # red
            (0.25, 0.85, 0.63),   # teal
            (0.99, 0.82, 0.10),   # yellow
            (0.38, 0.55, 0.99),   # blue
            (0.96, 0.49, 0.0),    # orange
        ]
        for idx, (px, py) in enumerate(self.plotted_points):
            sx, sy = to_screen(px, py)
            color = COLORS[idx % len(COLORS)]
            # Glow
            cr.set_source_rgba(*color, 0.2)
            cr.arc(sx, sy, 12, 0, 2 * math.pi)
            cr.fill()
            # Dot
            cr.set_source_rgb(*color)
            cr.arc(sx, sy, 7, 0, 2 * math.pi)
            cr.fill()
            # Index label
            cr.set_source_rgb(1, 1, 1)
            cr.set_font_size(9)
            label = str(idx + 1)
            ext = cr.text_extents(label)
            cr.move_to(sx - ext.width / 2, sy + ext.height / 2)
            cr.show_text(label)
            # Coordinate tooltip near point
            cr.set_font_size(10)
            cr.set_source_rgba(0.7, 0.9, 1.0, 0.85)
            cr.move_to(sx + 10, sy - 6)
            cr.show_text(f"({px}, {py})")

        # Store step for click mapping
        self._step = step
        self._cx = cx
        self._cy = cy
        self._cells = cells

    # ── Coordinate utilities ──────────────────────────────────────────────────

    def _screen_to_grid(self, sx, sy):
        """Convert screen px → grid (x, y), snapped to nearest integer."""
        step = getattr(self, "_step", 30)
        cx = getattr(self, "_cx", 400)
        cy = getattr(self, "_cy", 300)
        cells = getattr(self, "_cells", 10)
        gx = round((sx - cx) / step)
        gy = round(-(sy - cy) / step)
        gx = max(-cells, min(cells, gx))
        gy = max(-cells, min(cells, gy))
        return gx, gy

    # ── Canvas events ─────────────────────────────────────────────────────────

    def _canvas_click_cb(self, widget, event):
        if event.button != 1:
            return
        gx, gy = self._screen_to_grid(event.x, event.y)
        self._add_point(gx, gy)

    def _canvas_motion_cb(self, widget, event):
        gx, gy = self._screen_to_grid(event.x, event.y)
        if self.hover_point != (gx, gy):
            self.hover_point = (gx, gy)
            self.canvas.queue_draw()

    def _canvas_leave_cb(self, widget, event):
        self.hover_point = None
        self.canvas.queue_draw()

    # ── Point management ─────────────────────────────────────────────────────

    def _add_point(self, x, y):
        self.plotted_points.append((x, y))
        self._refresh_points_list()
        self.canvas.queue_draw()
        self._check_challenge_complete()

    def _manual_plot_cb(self, widget):
        try:
            x = int(self.x_entry.get_text().strip())
            y = int(self.y_entry.get_text().strip())
        except ValueError:
            self._flash_error(_("Please enter whole numbers only"))
            return
        cells = getattr(self, "_cells", 10)
        if abs(x) > cells or abs(y) > cells:
            self._flash_error(_(f"Values must be between -{cells} and {cells}"))
            return
        self.x_entry.set_text("")
        self.y_entry.set_text("")
        self._add_point(x, y)

    def _flash_error(self, msg):
        self.hint_label.set_markup(f'<span color="#ff6b6b">{msg}</span>')
        GLib.timeout_add(2500, lambda: self.hint_label.set_text(
            self.current_challenge["hint"] if self.current_challenge else ""
        ))

    def _undo_cb(self, btn):
        if self.plotted_points:
            self.plotted_points.pop()
            self._refresh_points_list()
            self.canvas.queue_draw()

    def _clear_cb(self, btn):
        self.plotted_points = []
        self.connected_lines = []
        self.success_label.hide()
        self._refresh_points_list()
        self.canvas.queue_draw()

    def _connect_toggled_cb(self, btn):
        self.connect_mode = btn.get_active()
        self.canvas.queue_draw()

    def _refresh_points_list(self):
        for child in self.points_list.get_children():
            self.points_list.remove(child)
        for idx, (x, y) in enumerate(self.plotted_points):
            row = Gtk.Label(label=f"  {idx+1}.  ({x:>3}, {y:>3})")
            row.get_style_context().add_class("point-row")
            row.set_xalign(0)
            self.points_list.pack_start(row, False, False, 0)
        self.points_list.show_all()

    # ── Challenge completion check ────────────────────────────────────────────

    def _check_challenge_complete(self):
        if not self.current_challenge or not self.current_challenge["points"]:
            return
        target = self.current_challenge["points"]
        plotted_set = set(self.plotted_points)
        target_set = set(map(tuple, target))
        matched = len(plotted_set & target_set)
        total = len(target_set)
        if matched == total:
            self.success_label.set_markup(
                f'<span color="#06d6a0">⭐ {_("Perfect!")} ⭐\n'
                f'{_("You matched all")} {total} {_("points!")}</span>'
            )
            self.success_label.show()
        elif matched > 0:
            self.success_label.set_markup(
                f'<span color="#ffd166">{matched}/{total} {_("points matched!")}</span>'
            )
            self.success_label.show()

    # ── Help ─────────────────────────────────────────────────────────────────

    def _help_cb(self, btn):
        msg = _("""\
How to use GraphIt:

🖱 Click anywhere on the grid to plot a point
⌨  Or type (x, y) in the boxes and press Plot
🔗 Toggle "Connect dots" to draw lines between points
↩  Undo removes the last point
🗑 Clear removes all points

The grid goes from -10 to +10 on both axes.
X → goes right (positive) or left (negative)
Y ↑ goes up (positive) or down (negative)

Try the challenges — match the ghost shape
by plotting the right coordinates!
""")
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=_("GraphIt — Help")
        )
        dialog.format_secondary_text(msg)
        dialog.run()
        dialog.destroy()

    # ── Journal persistence ───────────────────────────────────────────────────

    def read_file(self, file_path):
        """Load state from Sugar Journal."""
        if not os.path.exists(file_path):
            return
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            state = data.get("state", {})
            self.plotted_points = [tuple(p) for p in state.get("points", [])]
            self.challenge_index = state.get("challenge_index", 0)
            self.connect_mode = state.get("connect_mode", False)
            self.connect_toggle.set_active(self.connect_mode)
            self._load_challenge(self.challenge_index)
            # Restore points after loading challenge (which clears them)
            self.plotted_points = [tuple(p) for p in state.get("points", [])]
            self._refresh_points_list()
            self.canvas.queue_draw()
        except Exception as e:
            print(f"GraphIt read_file error: {e}")

    def write_file(self, file_path):
        """Save state to Sugar Journal."""
        import time
        try:
            data = {
                "metadata": {
                    "activity": "org.sugarlabs.GraphIt",
                    "timestamp": time.time(),
                },
                "state": {
                    "points": list(self.plotted_points),
                    "challenge_index": self.challenge_index,
                    "connect_mode": self.connect_mode,
                },
            }
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"GraphIt write_file error: {e}")