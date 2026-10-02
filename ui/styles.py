"""Apply a Theme to ttk widgets (base: clam, the most tintable builtin)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .theme import Theme

# Single family, three roles (skill: typography carries personality).
# Segoe UI exists on Windows; elsewhere Tk falls back gracefully.
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_ENTRY = (FONT_FAMILY, 12)
FONT_SMALL = (FONT_FAMILY, 10)


def apply_theme(root: tk.Tk, theme: Theme) -> ttk.Style:
    """Configure ttk styles + root background for `theme`. Idempotent."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(background=theme.bg)

    # -- base containers -------------------------------------------------
    style.configure("TFrame", background=theme.bg)
    style.configure(
        "TLabel",
        background=theme.bg,
        foreground=theme.fg,
        font=FONT_BODY,
    )
    style.configure(
        "Title.TLabel",
        background=theme.bg,
        foreground=theme.fg,
        font=FONT_TITLE,
    )
    style.configure(
        "Muted.TLabel",
        background=theme.bg,
        foreground=theme.muted,
        font=FONT_SMALL,
    )

    # -- buttons: quiet default, one loud accent --------------------------
    style.configure(
        "TButton",
        background=theme.surface,
        foreground=theme.fg,
        bordercolor=theme.border,
        lightcolor=theme.surface,
        darkcolor=theme.surface,
        padding=(12, 6),
        font=FONT_BODY,
    )
    style.map(
        "TButton",
        background=[("disabled", theme.surface), ("pressed", theme.border)],
        foreground=[("disabled", theme.muted)],
    )
    style.configure(
        "Accent.TButton",
        background=theme.action,
        foreground=theme.action_fg,
        bordercolor=theme.action,
        lightcolor=theme.action,
        darkcolor=theme.action,
        padding=(14, 6),
        font=FONT_BODY,
    )
    style.map(
        "Accent.TButton",
        background=[("disabled", theme.border), ("pressed", theme.action_active)],
        foreground=[("disabled", theme.muted)],
    )

    # -- inputs ------------------------------------------------------------
    style.configure(
        "TEntry",
        fieldbackground=theme.surface,
        foreground=theme.fg,
        insertcolor=theme.fg,
        bordercolor=theme.border,
        lightcolor=theme.border,
        darkcolor=theme.border,
        padding=6,
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", theme.action)],
    )
    style.configure(
        "TCombobox",
        fieldbackground=theme.surface,
        background=theme.surface,
        foreground=theme.fg,
        arrowcolor=theme.muted,
        bordercolor=theme.border,
        lightcolor=theme.border,
        darkcolor=theme.border,
        padding=4,
    )
    # Dropdown listbox is a plain tk widget, not ttk:
    root.option_add("*TCombobox*Listbox.background", theme.surface)
    root.option_add("*TCombobox*Listbox.foreground", theme.fg)
    root.option_add("*TCombobox*Listbox.selectBackground", theme.select_bg)
    root.option_add("*TCombobox*Listbox.selectForeground", theme.select_fg)

    # -- table: the protagonist, zebra + quiet header ----------------------
    style.configure(
        "Treeview",
        background=theme.surface,
        fieldbackground=theme.surface,
        foreground=theme.fg,
        bordercolor=theme.border,
        rowheight=28,
        font=FONT_BODY,
    )
    style.configure(
        "Treeview.Heading",
        background=theme.bg,
        foreground=theme.muted,
        font=FONT_SMALL,
        relief="flat",
        padding=(6, 6),
    )
    style.map(
        "Treeview",
        background=[("selected", theme.select_bg)],
        foreground=[("selected", theme.select_fg)],
    )
    style.configure("Vertical.TScrollbar", background=theme.bg, troughcolor=theme.surface,
                    bordercolor=theme.bg, arrowcolor=theme.muted)
    style.configure(
        "Horizontal.TProgressbar",
        background=theme.action,
        troughcolor=theme.surface,
        bordercolor=theme.bg,
        lightcolor=theme.action,
        darkcolor=theme.action,
    )

    return style
