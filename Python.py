import math
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

# ============================================================
# SKILL GRAPH
# Modern CSS-inspired desktop UI built entirely with Python.
# Uses Tkinter only — no HTML, CSS, JavaScript or Flask.
#
# "CSS" features recreated in pure Tkinter:
#   • border-radius      -> smooth rounded polygons on Canvas
#   • :hover             -> animated colour / border / slide effects
#   • transition         -> small tween engine (Tweener)
#   • dropdown on hover  -> custom HoverSelect with a pop-up menu
# ============================================================

APP_NAME = "Skill Graph"
FONT = "Segoe UI"

# ----------------------------
# Color theme
# ----------------------------
BG = "#0b1120"
BG_LIGHT = "#111827"
CARD = "#172033"
CARD_LIGHT = "#1e293b"
BORDER = "#2b3953"

WHITE = "#f8fafc"
TEXT = "#dbe4f0"
MUTED = "#94a3b8"

BLUE = "#3b82f6"
BLUE_HOVER = "#2563eb"
BLUE_SOFT = "#172f59"

CYAN = "#22d3ee"
PURPLE = "#8b5cf6"
GREEN = "#22c55e"
AMBER = "#f59e0b"

SKILLS = {
    "Software Development":
        "Learn C/C++, Python or Java, data structures, algorithms, "
        "Git, databases and web/application development.",

    "Artificial Intelligence":
        "Learn Python, mathematics, statistics, machine learning, "
        "neural networks, data handling and AI frameworks.",

    "Data Science":
        "Learn Python, SQL, statistics, data visualization, Excel, "
        "data analysis and machine learning.",

    "Cybersecurity":
        "Learn networking, Linux, operating systems, security "
        "fundamentals, cryptography and ethical security practices.",

    "UI/UX Design":
        "Learn design principles, typography, color theory, Figma, "
        "user research, wireframing and prototyping.",

    "Business / Entrepreneurship":
        "Learn business fundamentals, market research, communication, "
        "finance, marketing and product development."
}

EDUCATION_LEVELS = [
    "School",
    "Intermediate / 12th",
    "B.Tech / Engineering",
    "Degree",
    "Diploma",
    "Other"
]


# ============================================================
# Helpers
# ============================================================

def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    """Blend two hex colours. t=0 -> c1, t=1 -> c2."""
    t = max(0.0, min(1.0, t))
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return "#%02x%02x%02x" % tuple(
        int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)
    )


def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    return 4 * t * t * t if t < 0.5 else 1 - ((-2 * t + 2) ** 3) / 2


def ease_out_back(t):
    c1 = 0.9
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def rounded_points(x1, y1, x2, y2, r):
    """Point list for a smooth rounded rectangle (use smooth=True)."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    return [
        x1 + r, y1, x1 + r, y1,
        x2 - r, y1, x2 - r, y1,
        x2, y1,
        x2, y1 + r, x2, y1 + r,
        x2, y2 - r, x2, y2 - r,
        x2, y2,
        x2 - r, y2, x2 - r, y2,
        x1 + r, y2, x1 + r, y2,
        x1, y2,
        x1, y2 - r, x1, y2 - r,
        x1, y1 + r, x1, y1 + r,
        x1, y1,
    ]


def pointer_inside(widget, margin=0):
    try:
        x, y = widget.winfo_pointerxy()
        left = widget.winfo_rootx() - margin
        top = widget.winfo_rooty() - margin
        right = widget.winfo_rootx() + widget.winfo_width() + margin
        bottom = widget.winfo_rooty() + widget.winfo_height() + margin
    except tk.TclError:
        return False
    return left <= x < right and top <= y < bottom


def autowrap(container, label, pad=4, maximum=None):
    """Keep a label's wraplength in sync with its container's width."""
    last = {"w": None}

    def fit(event):
        width = max(160, event.width - pad)
        if maximum:
            width = min(width, maximum)
        if last["w"] != width:
            last["w"] = width
            label.configure(wraplength=width)

    container.bind("<Configure>", fit, add="+")


# ============================================================
# Animation engine  (CSS "transition")
# ============================================================

class Tweener:
    def __init__(self, widget):
        self.widget = widget
        self.jobs = {}

    def run(self, key, start, end, duration, step,
            done=None, ease=ease_out):
        self.cancel(key)

        if duration <= 0 or start == end:
            step(end)
            if done:
                done()
            return

        began = time.perf_counter()

        def tick():
            self.jobs.pop(key, None)
            try:
                if not self.widget.winfo_exists():
                    return
                progress = min(1.0, (time.perf_counter() - began) / duration)
                step(start + (end - start) * ease(progress))
                if progress < 1.0:
                    self.jobs[key] = self.widget.after(16, tick)
                elif done:
                    done()
            except tk.TclError:
                pass

        tick()

    def cancel(self, key):
        job = self.jobs.pop(key, None)
        if job is not None:
            try:
                self.widget.after_cancel(job)
            except tk.TclError:
                pass


# ============================================================
# Hover detection that works for a widget AND all its children
# ============================================================

class HoverMixin:

    def init_hover(self):
        self._inside = False
        self._bind_hover(self)

    def _bind_hover(self, widget):
        widget.bind("<Enter>", self._hover_event, add="+")
        widget.bind("<Leave>", self._hover_event, add="+")
        for child in widget.winfo_children():
            self._bind_hover(child)

    def _hover_event(self, _event=None):
        self.after(10, self.hover_eval)

    def _in_tree(self, widget):
        while widget is not None:
            if widget is self:
                return True
            widget = getattr(widget, "master", None)
        return False

    def hover_eval(self):
        try:
            if not self.winfo_exists():
                return
            x, y = self.winfo_pointerxy()
            under = self.winfo_containing(x, y)
        except (tk.TclError, KeyError):
            return

        inside = under is not None and self._in_tree(under)
        if inside != self._inside:
            self._inside = inside
            self.on_hover(inside)

    def on_hover(self, inside):
        pass


# ============================================================
# Rounded card  (CSS "border-radius" + ":hover")
# ============================================================

class RoundedBox(HoverMixin, tk.Canvas):
    """A Canvas that draws a rounded rectangle and hosts an inner Frame."""

    hoverables = []

    def __init__(self, parent, radius=20, fill=CARD, outline=BORDER,
                 outer_bg=BG, hover_fill=None, hover_outline=None,
                 focus_outline=CYAN, auto_height=True, **kw):
        super().__init__(
            parent, bg=outer_bg, highlightthickness=0, bd=0, height=2, **kw
        )

        self.radius = radius
        self.base_fill = fill
        self.base_outline = outline
        self.hover_fill = hover_fill or fill
        self.hover_outline = hover_outline or outline
        self.focus_outline = focus_outline
        self.pulse_color = CYAN

        self.level = {"h": 0.0, "f": 0.0, "p": 0.0}
        self.cur_fill = fill
        self.cur_outline = outline
        self.links = []
        self.tw = Tweener(self)

        self.pad = int(math.ceil(radius * 0.32)) + 1
        self.auto_height = auto_height
        self._wh = (0, 0)

        self.inner = tk.Frame(self, bg=fill)
        self.win = self.create_window(
            self.pad, self.pad, window=self.inner, anchor="nw"
        )

        self.bind("<Configure>", self._on_configure)
        if auto_height:
            self.inner.bind("<Configure>", lambda e: self._sync_height())
            self.after_idle(self._sync_height)

    # ---------- geometry ----------

    def _on_configure(self, event):
        self._wh = (event.width, event.height)
        self.itemconfigure(self.win, width=max(1, event.width - 2 * self.pad))
        self._draw()

    def _sync_height(self):
        try:
            wanted = self.inner.winfo_reqheight() + 2 * self.pad
            if wanted != int(float(self.cget("height"))):
                self.configure(height=wanted)
        except tk.TclError:
            pass

    def _draw(self):
        w, h = self._wh
        if w < 4 or h < 4:
            return
        self.delete("shape")
        self.create_polygon(
            rounded_points(1, 1, w - 1, h - 1, self.radius),
            smooth=True,
            fill=self.cur_fill,
            outline=self.cur_outline,
            width=1,
            tags="shape"
        )
        self.tag_lower("shape")

    # ---------- colour state ----------

    def _recolor(self, old, new):
        def walk(widget):
            try:
                if str(widget.cget("bg")) == old:
                    widget.configure(bg=new)
            except tk.TclError:
                pass
            for child in widget.winfo_children():
                walk(child)
        walk(self.inner)

    def _apply(self):
        h = self.level["h"]
        f = self.level["f"]
        p = self.level["p"]

        fill = mix(self.base_fill, self.hover_fill, h)
        outline = mix(self.base_outline, self.hover_outline, h)
        outline = mix(outline, self.focus_outline, f)
        outline = mix(outline, self.pulse_color, p)

        if fill != self.cur_fill:
            self._recolor(self.cur_fill, fill)
            self.cur_fill = fill
        self.cur_outline = outline

        self.itemconfigure("shape", fill=fill, outline=outline)

        for link in self.links:
            link.set_level(h)

    def _tween(self, key, target, duration):
        def step(value):
            self.level[key] = value
            self._apply()
        self.tw.run(key, self.level[key], target, duration, step)

    # ---------- public effects ----------

    def on_hover(self, inside):
        self._tween("h", 1.0 if inside else 0.0, 0.22)

    def set_focus(self, on):
        self._tween("f", 1.0 if on else 0.0, 0.2)

    def pulse(self, color=CYAN, duration=1.2):
        self.pulse_color = color

        def step(value):
            self.level["p"] = value
            self._apply()
        self.tw.run("p", 1.0, 0.0, duration, step)

    def enable_hover(self):
        self.init_hover()
        RoundedBox.hoverables.append(self)

    @classmethod
    def refresh_hovers(cls):
        alive = []
        for box in cls.hoverables:
            try:
                if box.winfo_exists():
                    alive.append(box)
                    box.hover_eval()
            except tk.TclError:
                pass
        cls.hoverables = alive


# ============================================================
# Small rounded pieces
# ============================================================

class Pill(tk.Canvas):
    """Rounded badge / tag with optional hover colour change."""

    def __init__(self, parent, text, fill=BLUE_SOFT, fg="#93c5fd",
                 font=(FONT, 8, "bold"), outer_bg=CARD, padx=11, pady=6,
                 radius=None, hover_fill=None, hover_fg=WHITE,
                 self_hover=False):
        measure = tkfont.Font(font=font)
        w = measure.measure(text) + 2 * padx
        h = measure.metrics("linespace") + 2 * pady

        super().__init__(
            parent, width=w, height=h, bg=outer_bg,
            highlightthickness=0, bd=0
        )

        self.fill = fill
        self.fg = fg
        self.hover_fill = hover_fill or mix(fill, CYAN, 0.32)
        self.hover_fg = hover_fg
        self.level = 0.0
        self.tw = Tweener(self)

        r = radius if radius is not None else h / 2
        self.shape = self.create_polygon(
            rounded_points(1, 1, w - 1, h - 1, r),
            smooth=True, fill=fill, outline=""
        )
        self.label = self.create_text(
            w / 2, h / 2, text=text, fill=fg, font=font
        )

        if self_hover:
            self.bind("<Enter>", lambda e: self._go(1.0))
            self.bind("<Leave>", lambda e: self._go(0.0))

    def set_level(self, value):
        self.level = value
        self.itemconfigure(
            self.shape, fill=mix(self.fill, self.hover_fill, value)
        )
        self.itemconfigure(
            self.label, fill=mix(self.fg, self.hover_fg, value)
        )

    def _go(self, target):
        self.tw.run("lv", self.level, target, 0.16, self.set_level)


class AccentBar(tk.Canvas):
    """Fully rounded coloured bar."""

    def __init__(self, parent, color=CYAN, width=8, height=10,
                 outer_bg=CARD):
        super().__init__(
            parent, width=width, height=height, bg=outer_bg,
            highlightthickness=0, bd=0
        )
        self.color = color
        self.bind("<Configure>", self._draw)

    def _draw(self, _event=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 2 or h < 2:
            return
        self.delete("bar")
        self.create_polygon(
            rounded_points(0, 0, w, h, min(w, h) / 2),
            smooth=True, fill=self.color, outline="", tags="bar"
        )

    def set_color(self, color):
        self.color = color
        self.itemconfigure("bar", fill=color)


class RoundedButton(tk.Canvas):
    """Pill-style button: colour fade, glow border, sliding arrow, press."""

    def __init__(self, parent, text, command, fill=BLUE,
                 hover_fill=BLUE_HOVER, outer_bg=CARD, height=56,
                 radius=18, font=(FONT, 11, "bold")):
        super().__init__(
            parent, height=height, bg=outer_bg, highlightthickness=0,
            bd=0, cursor="hand2"
        )
        self.text = text
        self.command = command
        self.fill = fill
        self.hover_fill = hover_fill
        self.radius = radius
        self.font = tkfont.Font(font=font)
        self.font_spec = font

        self.lv = {"h": 0.0, "p": 0.0}
        self.tw = Tweener(self)
        self._h = height
        self._text_x = 0
        self._arrow_x = 0

        self.bind("<Configure>", self._layout)
        self.bind("<Enter>", lambda e: self._go("h", 1.0, 0.2))
        self.bind("<Leave>", lambda e: self._go("h", 0.0, 0.25))
        self.bind("<ButtonPress-1>", lambda e: self._go("p", 1.0, 0.08))
        self.bind("<ButtonRelease-1>", self._release)

    def _go(self, key, target, duration):
        def step(value):
            self.lv[key] = value
            self._apply()
        self.tw.run(key, self.lv[key], target, duration, step)

    def _release(self, event):
        self._go("p", 0.0, 0.18)
        if 0 <= event.x < self.winfo_width() and 0 <= event.y < self._h:
            self.command()

    def _layout(self, _event=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 8:
            return
        self._h = h
        self.delete("all")

        self.create_polygon(
            rounded_points(2, 2, w - 2, h - 2, self.radius),
            smooth=True, fill=self.fill, outline=self.fill,
            width=2, tags="shape"
        )

        text_w = self.font.measure(self.text)
        arrow_w = self.font.measure("→")
        gap = 14
        left = (w - (text_w + gap + arrow_w)) / 2

        self._text_x = left + text_w / 2
        self._arrow_x = left + text_w + gap + arrow_w / 2

        self.create_text(
            self._text_x, h / 2, text=self.text, fill=WHITE,
            font=self.font_spec, tags="txt"
        )
        self.create_text(
            self._arrow_x, h / 2, text="→", fill=WHITE,
            font=self.font_spec, tags="arrow"
        )
        self._apply()

    def _apply(self):
        if not self.find_withtag("shape"):
            return
        v, p = self.lv["h"], self.lv["p"]
        fill = mix(mix(self.fill, self.hover_fill, v), "#000000", 0.2 * p)
        edge = mix(fill, CYAN, 0.75 * v)
        self.itemconfigure("shape", fill=fill, outline=edge)

        mid = self._h / 2
        self.coords("txt", self._text_x - 4 * v, mid)
        self.coords("arrow", self._arrow_x + 8 * v - 2 * p, mid)


class ToggleChip(tk.Canvas):
    """Rounded checkbox-style chip with animated check."""

    def __init__(self, parent, text, variable, outer_bg=CARD,
                 height=52, radius=16):
        super().__init__(
            parent, height=height, bg=outer_bg, highlightthickness=0,
            bd=0, cursor="hand2"
        )
        self.text = text
        self.var = variable
        self.radius = radius
        self.lv = {"h": 0.0, "p": 1.0 if variable.get() else 0.0}
        self.tw = Tweener(self)

        self.bind("<Configure>", self._layout)
        self.bind("<Enter>", lambda e: self._go("h", 1.0, 0.18))
        self.bind("<Leave>", lambda e: self._go("h", 0.0, 0.22))
        self.bind("<ButtonRelease-1>", self._toggle)

        variable.trace_add("write", lambda *a: self._sync())

    def _toggle(self, event):
        if 0 <= event.x < self.winfo_width() and 0 <= event.y < self.winfo_height():
            self.var.set(not self.var.get())

    def _sync(self):
        try:
            self._go("p", 1.0 if self.var.get() else 0.0, 0.22)
        except tk.TclError:
            pass

    def _go(self, key, target, duration):
        def step(value):
            self.lv[key] = value
            self._apply()
        self.tw.run(key, self.lv[key], target, duration, step)

    def _layout(self, _event=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 8:
            return
        self.delete("all")
        self.create_polygon(
            rounded_points(1, 1, w - 1, h - 1, self.radius),
            smooth=True, fill=CARD_LIGHT, outline=BORDER, tags="shape"
        )
        self.create_oval(
            14, h / 2 - 10, 34, h / 2 + 10,
            fill=CARD_LIGHT, outline=MUTED, width=2, tags="dot"
        )
        self.create_text(
            24, h / 2, text="✓", font=(FONT, 9, "bold"), tags="tick"
        )
        self.create_text(
            50, h / 2, text=self.text, anchor="w",
            font=(FONT, 10), tags="lbl"
        )
        self._apply()

    def _apply(self):
        if not self.find_withtag("shape"):
            return
        h, p = self.lv["h"], self.lv["p"]
        fill = mix(mix(CARD_LIGHT, BLUE_SOFT, 0.55 * h), BLUE_SOFT, p)
        edge = mix(mix(BORDER, CYAN, 0.5 * h), BLUE, p)
        dot_fill = mix(fill, CYAN, p)
        dot_edge = mix(MUTED, CYAN, max(0.6 * h, p))

        self.itemconfigure("shape", fill=fill, outline=edge)
        self.itemconfigure("dot", fill=dot_fill, outline=dot_edge)
        self.itemconfigure("tick", fill=mix(fill, BG, p))
        self.itemconfigure("lbl", fill=mix(TEXT, WHITE, max(h, p)))


class OptionRow(tk.Canvas):
    """One rounded row in a hover dropdown."""

    def __init__(self, parent, text, on_pick, outer_bg=CARD_LIGHT,
                 height=40):
        super().__init__(
            parent, height=height, bg=outer_bg, highlightthickness=0,
            bd=0, cursor="hand2"
        )
        self.text = text
        self.outer_bg = outer_bg
        self.selected = False
        self.lv = 0.0
        self.tw = Tweener(self)

        self.bind("<Configure>", self._layout)
        self.bind("<Enter>", lambda e: self._go(1.0))
        self.bind("<Leave>", lambda e: self._go(0.0))
        self.bind("<ButtonRelease-1>", lambda e: on_pick(self.text))

    def _go(self, target):
        self.tw.run("h", self.lv, target, 0.14, self._set)

    def _set(self, value):
        self.lv = value
        self._apply()

    def set_selected(self, flag):
        self.selected = flag
        self._apply()

    def _layout(self, _event=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 8:
            return
        self.delete("all")
        self.create_polygon(
            rounded_points(0, 0, w, h, 12),
            smooth=True, fill=self.outer_bg, outline="", tags="shape"
        )
        self.create_text(
            16, h / 2, text=self.text, anchor="w",
            font=(FONT, 10), tags="txt"
        )
        self.create_text(
            w - 16, h / 2, text="✓", anchor="e",
            font=(FONT, 10, "bold"), tags="tick"
        )
        self._apply()

    def _apply(self):
        if not self.find_withtag("shape"):
            return
        v = self.lv
        base_fg = "#67e8f9" if self.selected else TEXT
        self.itemconfigure(
            "shape", fill=mix(self.outer_bg, BLUE_SOFT, v)
        )
        self.itemconfigure("txt", fill=mix(base_fg, WHITE, v))
        self.itemconfigure(
            "tick", text="✓" if self.selected else "", fill=CYAN
        )
        self.coords("txt", 16 + 7 * v, self.winfo_height() / 2)


class HoverSelect(tk.Canvas):
    """
    Rounded dropdown whose options pop up when the cursor hovers over it
    and tuck away again when the cursor leaves.
    """

    def __init__(self, parent, app, variable, values, placeholder,
                 outer_bg=CARD, height=54, radius=16):
        super().__init__(
            parent, height=height, bg=outer_bg, highlightthickness=0,
            bd=0, cursor="hand2"
        )
        self.app = app
        self.var = variable
        self.values = values
        self.placeholder = placeholder
        self.outer_bg = outer_bg
        self.radius = radius

        self.lv = {"h": 0.0, "o": 0.0, "p": 0.0}
        self.tw = Tweener(self)

        self.popup = None
        self.popup_full = 0
        self.pop_h = 0.0
        self.rows = []
        self.is_open = False
        self.opens_up = False
        self.anchor_xy = (0, 0, 0)
        self.poll_job = None

        self.bind("<Configure>", self._layout)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", lambda e: self._refresh_hover())
        self.bind("<ButtonRelease-1>", lambda e: self.open())

        variable.trace_add("write", lambda *a: self._update_text())

    # ---------- drawing ----------

    def _setter(self, key):
        def step(value):
            self.lv[key] = value
            self._apply()
        return step

    def _layout(self, _event=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 8:
            return
        self.delete("all")
        self.create_polygon(
            rounded_points(1, 1, w - 1, h - 1, self.radius),
            smooth=True, fill=CARD_LIGHT, outline=BORDER,
            width=1, tags="shape"
        )
        self.create_text(
            20, h / 2, anchor="w", text="", font=(FONT, 11), tags="txt"
        )
        self.create_line(
            0, 0, 0, 0, 0, 0, width=2, capstyle="round",
            joinstyle="round", tags="chev"
        )
        self._update_text()
        self._apply()

    def _update_text(self):
        try:
            value = self.var.get()
            self.itemconfigure(
                "txt",
                text=value or self.placeholder,
                fill=WHITE if value else MUTED
            )
        except tk.TclError:
            pass

    def _apply(self):
        if not self.find_withtag("chev"):
            return
        w, h = self.winfo_width(), self.winfo_height()
        hv, op, pl = self.lv["h"], self.lv["o"], self.lv["p"]

        fill = mix(CARD_LIGHT, BLUE_SOFT, 0.5 * hv)
        edge = mix(mix(BORDER, CYAN, 0.5 * hv), CYAN, 0.5 * op)
        edge = mix(edge, GREEN, pl)
        self.itemconfigure("shape", fill=fill, outline=edge)

        cx, cy = w - 30, h / 2
        s = 1 - 2 * op
        self.coords(
            "chev",
            cx - 6, cy - 3 * s, cx, cy + 3 * s, cx + 6, cy - 3 * s
        )
        self.itemconfigure("chev", fill=mix(MUTED, CYAN, max(hv, op)))

    # ---------- hover state ----------

    def _refresh_hover(self):
        target = 1.0 if (self.is_open or pointer_inside(self)) else 0.0
        self.tw.run("h", self.lv["h"], target, 0.2, self._setter("h"))

    def _on_enter(self, _event=None):
        self._refresh_hover()
        self.after(80, self._maybe_open)

    def _maybe_open(self):
        if not self.is_open and pointer_inside(self):
            self.open()

    # ---------- popup ----------

    def _build_popup(self):
        if self.popup is not None:
            return

        self.popup = RoundedBox(
            self.app, radius=18, fill=CARD_LIGHT,
            outline=mix(BORDER, CYAN, 0.55),
            outer_bg=self.outer_bg, auto_height=False
        )

        last = len(self.values) - 1
        for index, value in enumerate(self.values):
            row = OptionRow(self.popup.inner, value, self.choose)
            row.pack(
                fill="x", padx=6,
                pady=(6 if index == 0 else 2, 6 if index == last else 2)
            )
            self.rows.append(row)

        self.popup.update_idletasks()
        self.popup_full = (
            self.popup.inner.winfo_reqheight() + 2 * self.popup.pad
        )

    def _pop_step(self, value):
        self.pop_h = value
        height = max(1, int(value))
        ax, ay, fh = self.anchor_xy
        y = ay - 4 - height if self.opens_up else ay + fh + 4
        try:
            self.popup.place_configure(y=y, height=height)
        except tk.TclError:
            pass

    def open(self):
        if self.is_open:
            return

        self.app.close_popups(except_=self)
        self._build_popup()

        current = self.var.get()
        for row in self.rows:
            row.set_selected(row.text == current)

        self.is_open = True
        self.update_idletasks()

        ax = self.winfo_rootx() - self.app.winfo_rootx()
        ay = self.winfo_rooty() - self.app.winfo_rooty()
        fw, fh = self.winfo_width(), self.winfo_height()
        below = self.app.winfo_height() - (ay + fh)

        self.opens_up = self.popup_full + 12 > below and ay > below
        self.anchor_xy = (ax, ay, fh)

        self.popup.place(x=ax, y=ay + fh + 4, width=fw, height=1)
        self.popup.lift()

        self.tw.run(
            "pop", self.pop_h, self.popup_full, 0.24,
            self._pop_step, ease=ease_out_back
        )
        self.tw.run("o", self.lv["o"], 1.0, 0.2, self._setter("o"))
        self._refresh_hover()
        self._poll()

    def close(self):
        if not self.is_open:
            return
        self.is_open = False

        if self.poll_job is not None:
            try:
                self.after_cancel(self.poll_job)
            except tk.TclError:
                pass
            self.poll_job = None

        self.tw.run(
            "pop", self.pop_h, 0.0, 0.15, self._pop_step,
            done=self._hide_popup
        )
        self.tw.run("o", self.lv["o"], 0.0, 0.18, self._setter("o"))
        self._refresh_hover()

    def _hide_popup(self):
        if not self.is_open and self.popup is not None:
            self.popup.place_forget()

    def _in_zone(self):
        try:
            x, y = self.winfo_pointerxy()
            fx1, fy1 = self.winfo_rootx(), self.winfo_rooty()
            fx2, fy2 = fx1 + self.winfo_width(), fy1 + self.winfo_height()
            px1, py1 = self.popup.winfo_rootx(), self.popup.winfo_rooty()
            px2 = px1 + self.popup.winfo_width()
            py2 = py1 + self.popup.winfo_height()
        except tk.TclError:
            return False

        margin = 6
        left = min(fx1, px1) - margin
        top = min(fy1, py1) - margin
        right = max(fx2, px2) + margin
        bottom = max(fy2, py2) + margin
        return left <= x <= right and top <= y <= bottom

    def _poll(self):
        self.poll_job = None
        if not self.is_open:
            return
        if not self._in_zone():
            self.close()
            return
        self.poll_job = self.after(110, self._poll)

    def choose(self, value):
        self.var.set(value)
        self.tw.run("p", 1.0, 0.0, 0.9, self._setter("p"))
        self.close()


class RoundedEntry(RoundedBox):
    """Text field with rounded corners and an animated focus ring."""

    def __init__(self, parent, variable, outer_bg=CARD):
        super().__init__(
            parent, radius=16, fill=CARD_LIGHT, outline=BORDER,
            hover_outline=mix(BORDER, CYAN, 0.45),
            focus_outline=CYAN, outer_bg=outer_bg
        )

        self.entry = tk.Entry(
            self.inner,
            textvariable=variable,
            bg=CARD_LIGHT,
            fg=WHITE,
            insertbackground=CYAN,
            selectbackground=BLUE,
            selectforeground=WHITE,
            font=(FONT, 11),
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.entry.pack(fill="x", padx=14, pady=14)

        self.entry.bind("<FocusIn>", lambda e: self.set_focus(True))
        self.entry.bind("<FocusOut>", lambda e: self.set_focus(False))
        self.bind("<Button-1>", lambda e: self.entry.focus_set())
        self.inner.bind("<Button-1>", lambda e: self.entry.focus_set())

        self.enable_hover()


class SlimScrollbar(tk.Canvas):
    """Thin rounded scrollbar."""

    def __init__(self, parent, command, width=12, outer_bg=BG):
        super().__init__(
            parent, width=width, bg=outer_bg,
            highlightthickness=0, bd=0
        )
        self.command = command
        self.first = 0.0
        self.last = 1.0
        self.level = 0.0
        self.drag_offset = None
        self.tw = Tweener(self)

        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", lambda e: self._go(1.0))
        self.bind("<Leave>", self._leave)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", self._release)

    def set(self, first, last):
        self.first, self.last = float(first), float(last)
        self._draw()

    def _go(self, target):
        self.tw.run("h", self.level, target, 0.18, self._set_level)

    def _set_level(self, value):
        self.level = value
        self._draw()

    def _leave(self, _event):
        if self.drag_offset is None:
            self._go(0.0)

    def _geometry(self):
        height = max(1, self.winfo_height())
        span = self.last - self.first
        length = max(40.0, span * height)
        travel = max(1.0, height - length)
        denom = max(1e-6, 1 - span)
        top = self.first / denom * travel
        return top, top + length, travel, denom

    def _draw(self):
        self.delete("thumb")
        if self.last - self.first >= 0.999:
            return
        width = self.winfo_width()
        top, bottom, _, _ = self._geometry()
        self.create_polygon(
            rounded_points(3, top + 1, width - 3, bottom - 1,
                           (width - 6) / 2),
            smooth=True,
            fill=mix(BORDER, BLUE, 0.75 * self.level),
            outline="", tags="thumb"
        )

    def _press(self, event):
        top, bottom, _, _ = self._geometry()
        if top <= event.y <= bottom:
            self.drag_offset = event.y - top
        else:
            self.drag_offset = (bottom - top) / 2
            self._drag(event)

    def _drag(self, event):
        if self.drag_offset is None:
            return
        _, _, travel, denom = self._geometry()
        position = max(0.0, min(travel, event.y - self.drag_offset))
        self.command("moveto", position / travel * denom)

    def _release(self, event):
        self.drag_offset = None
        if not pointer_inside(self):
            self._go(0.0)


# ============================================================
# Application
# ============================================================

class SkillGraph(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Skill Graph — Career Roadmap")
        self.geometry("1080x820")
        self.minsize(900, 680)
        self.configure(bg=BG)

        self.education = tk.StringVar()
        self.interest = tk.StringVar()
        self.career = tk.StringVar()

        self.strength_vars = {
            "Problem Solving": tk.BooleanVar(),
            "Creativity": tk.BooleanVar(),
            "Communication": tk.BooleanVar(),
            "Mathematics": tk.BooleanVar()
        }

        self.tw = Tweener(self)
        self.selects = []
        self.roadmap_area = None
        self.footer = None
        self.reveal_jobs = []

        self.create_interface()

        self.bind("<Escape>", lambda e: self.close_popups())
        self.after(120, self.play_intro)
        self.after(200, self._breathe)

    # ========================================================
    # Small animation helpers
    # ========================================================

    def fade_in(self, label, final, start, delay, duration=0.9):
        label.configure(fg=start)

        def go():
            self.tw.run(
                ("fade", str(label)), 0.0, 1.0, duration,
                lambda v: label.configure(fg=mix(start, final, v))
            )

        self.after(delay, go)

    def play_intro(self):
        self.form_card.pulse(CYAN, 1.6)

    def _breathe(self):
        t = time.perf_counter()
        a = (math.sin(t * 1.6) + 1) / 2
        b = (math.sin(t * 1.1 + 1.3) + 1) / 2
        self.accent.set_color(mix(mix(BLUE, PURPLE, a), CYAN, b))
        self.after(50, self._breathe)

    def smooth_scroll_to(self, target_y, duration=0.9):
        start = self.canvas.canvasy(0)

        def step(value):
            self.content.update_idletasks()
            total = max(1, self.content.winfo_reqheight())
            self.canvas.yview_moveto(max(0.0, value) / total)

        self.tw.run("scroll", start, target_y, duration, step,
                    ease=ease_in_out)

    def close_popups(self, except_=None):
        for select in self.selects:
            if select is not except_:
                select.close()

    # ========================================================
    # Main interface
    # ========================================================

    def create_interface(self):

        # ----------------------------
        # Top navigation bar
        # ----------------------------
        header = tk.Frame(self, bg=BG, height=78)
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=BG)
        brand.pack(side="left", padx=42)

        tk.Label(
            brand, text="SKILL", bg=BG, fg=WHITE,
            font=(FONT, 23, "bold")
        ).pack(side="left")

        tk.Label(
            brand, text=" GRAPH", bg=BG, fg=CYAN,
            font=(FONT, 23, "bold")
        ).pack(side="left")

        Pill(
            header, "CAREER INTELLIGENCE",
            fill=CARD, fg=MUTED, font=(FONT, 9, "bold"),
            outer_bg=BG, padx=16, pady=8,
            hover_fill=BLUE_SOFT, hover_fg=CYAN, self_hover=True
        ).pack(side="right", padx=42)

        # ----------------------------
        # Hero (rounded panel)
        # ----------------------------
        hero_wrap = tk.Frame(self, bg=BG)
        hero_wrap.pack(fill="x", padx=40, pady=(0, 8))

        hero = RoundedBox(
            hero_wrap, radius=32, fill=BG_LIGHT, outline=BORDER,
            outer_bg=BG
        )
        hero.pack(fill="x")
        hi = hero.inner

        self.accent = AccentBar(
            hi, color=BLUE, width=110, height=6, outer_bg=BG_LIGHT
        )
        self.accent.pack(pady=(30, 16))

        kicker = tk.Label(
            hi, text="BUILD YOUR", bg=BG_LIGHT, fg=MUTED,
            font=(FONT, 11, "bold")
        )
        kicker.pack()

        title = tk.Label(
            hi, text="Career Roadmap.", bg=BG_LIGHT, fg=WHITE,
            font=(FONT, 38, "bold")
        )
        title.pack(pady=(2, 7))

        subtitle = tk.Label(
            hi,
            text=(
                "Turn your interests and strengths into a clear path of "
                "skills, projects and experience."
            ),
            bg=BG_LIGHT, fg=TEXT, font=(FONT, 12),
            wraplength=720, justify="center"
        )
        subtitle.pack(pady=(0, 34))

        self.fade_in(kicker, MUTED, BG_LIGHT, 100, 0.7)
        self.fade_in(title, WHITE, BG_LIGHT, 250, 0.9)
        self.fade_in(subtitle, TEXT, BG_LIGHT, 450, 0.9)

        # ----------------------------
        # Scrollable area
        # ----------------------------
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)

        self.scrollbar = SlimScrollbar(outer, command=self.canvas.yview)

        self.content = tk.Frame(self.canvas, bg=BG)

        self.window_id = self.canvas.create_window(
            (0, 0), window=self.content, anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=6)

        self.content.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.bind("<Configure>", self.resize_content)

        self.canvas.bind_all("<MouseWheel>", self.mouse_scroll)
        self.canvas.bind_all("<Button-4>", self.mouse_scroll)
        self.canvas.bind_all("<Button-5>", self.mouse_scroll)

        self.create_form()

    def resize_content(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def mouse_scroll(self, event):
        if getattr(event, "num", None) == 4:
            delta = 120
        elif getattr(event, "num", None) == 5:
            delta = -120
        else:
            delta = event.delta

        if abs(delta) >= 120:
            units = -int(delta / 120)
        else:
            units = -1 if delta > 0 else 1

        self.close_popups()
        self.canvas.yview_scroll(units, "units")
        self.after(40, RoundedBox.refresh_hovers)

    # ========================================================
    # Form
    # ========================================================

    def create_form(self):

        card = RoundedBox(
            self.content, radius=30, fill=CARD, outline=BORDER,
            outer_bg=BG
        )
        card.pack(fill="x", padx=75, pady=(30, 38))
        self.form_card = card
        body = card.inner

        # Heading
        heading_row = tk.Frame(body, bg=CARD)
        heading_row.pack(fill="x", padx=30, pady=(28, 25))

        Pill(
            heading_row, "01", fill=BLUE_SOFT, fg=CYAN,
            font=(FONT, 11, "bold"), outer_bg=CARD,
            padx=14, pady=10, radius=15
        ).pack(side="left", padx=(0, 14))

        heading_text = tk.Frame(heading_row, bg=CARD)
        heading_text.pack(side="left")

        tk.Label(
            heading_text, text="Create Your Career Roadmap",
            bg=CARD, fg=WHITE, font=(FONT, 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            heading_text,
            text="Tell us where you are and where you want to go.",
            bg=CARD, fg=MUTED, font=(FONT, 10)
        ).pack(anchor="w", pady=(3, 0))

        # Education (hover dropdown)
        self.add_label(body, "CURRENT EDUCATION")

        education_box = HoverSelect(
            body, self, self.education, EDUCATION_LEVELS,
            "Hover to choose your education"
        )
        education_box.pack(fill="x", padx=30, pady=(0, 22))
        self.selects.append(education_box)

        # Interest (hover dropdown)
        self.add_label(body, "AREA OF INTEREST")

        interest_box = HoverSelect(
            body, self, self.interest, list(SKILLS.keys()),
            "Hover to choose your area of interest"
        )
        interest_box.pack(fill="x", padx=30, pady=(0, 22))
        self.selects.append(interest_box)

        # Strengths
        self.add_label(body, "YOUR MAIN STRENGTHS")

        strength_frame = tk.Frame(body, bg=CARD)
        strength_frame.pack(fill="x", padx=25, pady=(0, 20))

        for index, (name, variable) in enumerate(
            self.strength_vars.items()
        ):
            chip = ToggleChip(strength_frame, name, variable)
            chip.grid(
                row=index // 2, column=index % 2,
                sticky="ew", padx=5, pady=5
            )

        strength_frame.columnconfigure(0, weight=1)
        strength_frame.columnconfigure(1, weight=1)

        # Career
        self.add_label(body, "CAREER YOU WANT TO EXPLORE")

        career_entry = RoundedEntry(body, self.career)
        career_entry.pack(fill="x", padx=30, pady=(0, 26))

        career_entry.entry.bind(
            "<Return>", lambda event: self.generate_roadmap()
        )

        # Button
        self.generate_button = RoundedButton(
            body, "GENERATE MY ROADMAP", self.generate_roadmap
        )
        self.generate_button.pack(fill="x", padx=30, pady=(0, 32))

    def add_label(self, parent, text):
        tk.Label(
            parent, text=text, bg=CARD, fg=MUTED,
            font=(FONT, 9, "bold")
        ).pack(anchor="w", padx=30, pady=(0, 8))

    # ========================================================
    # Roadmap generation
    # ========================================================

    def cancel_reveal(self):
        for job in self.reveal_jobs:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        self.reveal_jobs = []

    def generate_roadmap(self):

        education = self.education.get().strip()
        interest = self.interest.get().strip()
        career = self.career.get().strip()

        if not education or not interest or not career:
            self.form_card.pulse(AMBER, 0.9)
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all the required fields."
            )
            return

        strengths = [
            name
            for name, variable in self.strength_vars.items()
            if variable.get()
        ]

        self.close_popups()
        self.cancel_reveal()

        for widget in (self.roadmap_area, self.footer):
            if widget is not None:
                widget.destroy()

        self.roadmap_area = tk.Frame(self.content, bg=BG)
        self.roadmap_area.pack(fill="x", padx=75, pady=(0, 24))

        # Section heading
        top = tk.Frame(self.roadmap_area, bg=BG)
        top.pack(fill="x", pady=(0, 15))

        Pill(
            top, "02", fill=PURPLE, fg=WHITE, font=(FONT, 10, "bold"),
            outer_bg=BG, padx=13, pady=8, radius=12
        ).pack(side="left", padx=(0, 12))

        tk.Label(
            top, text="YOUR PERSONALIZED ROADMAP", bg=BG, fg=WHITE,
            font=(FONT, 17, "bold")
        ).pack(side="left")

        # Summary card
        summary = RoundedBox(
            self.roadmap_area, radius=24, fill=CARD, outline=BORDER,
            outer_bg=BG, hover_fill=CARD_LIGHT,
            hover_outline=mix(BORDER, CYAN, 0.65)
        )
        summary.pack(fill="x", pady=(0, 18))

        AccentBar(summary.inner, color=CYAN, width=8, outer_bg=CARD).pack(
            side="left", fill="y", padx=(20, 0), pady=22
        )

        summary_body = tk.Frame(summary.inner, bg=CARD)
        summary_body.pack(
            side="left", fill="both", expand=True, padx=22, pady=22
        )

        career_label = tk.Label(
            summary_body, text=career, bg=CARD, fg=WHITE,
            font=(FONT, 25, "bold"), justify="left", anchor="w"
        )
        career_label.pack(anchor="w")
        autowrap(summary_body, career_label)

        tk.Label(
            summary_body, text=f"{education}  •  {interest}",
            bg=CARD, fg=CYAN, font=(FONT, 10, "bold")
        ).pack(anchor="w", pady=(3, 10))

        summary_text = tk.Label(
            summary_body,
            text=(
                f"Based on your current level and interest, this roadmap "
                f"gives you a practical starting path for exploring "
                f"{career}."
            ),
            bg=CARD, fg=TEXT, font=(FONT, 10), wraplength=700,
            justify="left"
        )
        summary_text.pack(anchor="w")

        if strengths:
            strengths_label = tk.Label(
                summary_body,
                text="STRENGTHS  •  " + "   •   ".join(strengths),
                bg=CARD, fg=MUTED, font=(FONT, 9, "bold"),
                wraplength=700, justify="left"
            )
            strengths_label.pack(anchor="w", pady=(13, 0))

        summary.enable_hover()
        summary.pulse(CYAN, 1.2)

        # Footer
        self.footer = tk.Label(
            self.content, text="SKILL GRAPH  •  BUILD YOUR FUTURE",
            bg=BG, fg=MUTED, font=(FONT, 9, "bold")
        )
        self.footer.pack(pady=(0, 30))

        # Roadmap steps (revealed one after another)
        steps = [
            (
                "01", "BUILD YOUR FOUNDATION",
                "Start with the fundamentals required for your field. "
                "Focus on programming basics, logical thinking, "
                "mathematics and computer fundamentals.",
                ["Programming", "Logic", "Computer Fundamentals"]
            ),
            (
                "02", "LEARN CORE SKILLS",
                SKILLS.get(
                    interest,
                    "Develop the technical skills commonly used in your "
                    "chosen career."
                ),
                None
            ),
            (
                "03", "BUILD REAL PROJECTS",
                "Don't only watch tutorials. Build projects that "
                "demonstrate what you have learned.",
                ["Mini Projects", "GitHub", "Portfolio"]
            ),
            (
                "04", "GAIN EXPERIENCE",
                "Participate in hackathons, open-source projects, "
                "internships and college technical communities.",
                None
            ),
            (
                "05", "PREPARE FOR YOUR CAREER",
                "Build your resume, improve interview skills, "
                "practice technical questions and create a strong "
                "professional portfolio.",
                None
            ),
            (
                "06", "YOUR LONG-TERM GOAL",
                "Continue learning, specialize in a domain and "
                "regularly update your skills as the industry changes.",
                ["Specialize", "Keep Learning", "Stay Relevant"]
            ),
        ]

        for index, spec in enumerate(steps):
            job = self.after(
                220 + index * 130,
                lambda s=spec: self.add_step(*s)
            )
            self.reveal_jobs.append(job)

        self.update_idletasks()
        self.smooth_scroll_to(self.roadmap_area.winfo_y() - 14, 0.9)

    # ========================================================
    # Roadmap card
    # ========================================================

    def add_step(self, number, title, description, tags=None):

        if self.roadmap_area is None or not self.roadmap_area.winfo_exists():
            return

        step = RoundedBox(
            self.roadmap_area, radius=22, fill=CARD, outline=BORDER,
            outer_bg=BG, hover_fill=CARD_LIGHT,
            hover_outline=mix(BORDER, CYAN, 0.65)
        )
        step.pack(fill="x", pady=(6 + 24, 6))

        # Number badge (rounded, lights up with the card)
        badge = Pill(
            step.inner, number, fill=BLUE_SOFT, fg=CYAN,
            font=(FONT, 12, "bold"), outer_bg=CARD,
            padx=17, pady=15, radius=17,
            hover_fill=BLUE, hover_fg=WHITE
        )
        badge.pack(side="left", padx=(20, 0), pady=20, anchor="n")
        step.links.append(badge)

        body = tk.Frame(step.inner, bg=CARD)
        body.pack(side="left", fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            body, text=title, bg=CARD, fg=WHITE,
            font=(FONT, 12, "bold")
        ).pack(anchor="w", pady=(0, 7))

        desc = tk.Label(
            body, text=description, bg=CARD, fg=TEXT,
            font=(FONT, 10), wraplength=620, justify="left"
        )
        desc.pack(anchor="w")
        autowrap(body, desc)

        if tags:
            tags_frame = tk.Frame(body, bg=CARD)
            tags_frame.pack(anchor="w", pady=(12, 0))

            for tag in tags:
                Pill(
                    tags_frame, tag, fill=BLUE_SOFT, fg="#93c5fd",
                    font=(FONT, 8, "bold"), outer_bg=CARD,
                    padx=12, pady=6, self_hover=True
                ).pack(side="left", padx=(0, 7))

        step.enable_hover()
        step.pulse(CYAN, 1.1)

        def slide(value):
            try:
                step.pack_configure(pady=(6 + int(value), 6))
            except tk.TclError:
                pass

        self.tw.run(("slide", id(step)), 24, 0, 0.4, slide)


if __name__ == "__main__":
    app = SkillGraph()
    app.mainloop()
