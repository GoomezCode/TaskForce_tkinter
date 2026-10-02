"""Design tokens for the TaskForce Tkinter client (frontend-design skill).

Two themes only — Light ("Papel Operacional") and Dark ("Turno Noturno") —
sharing a single action hue so the identity survives the toggle.

Deliberately avoids the generic defaults flagged by the skill:
no cream #F4F1EA + terracotta, no near-black #0B0B0B + acid green,
no gradient washes, no ALL-CAPS eyebrows.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Theme:
    name: str  # "light" | "dark"
    label: str  # human label for the toggle
    # Core surfaces
    bg: str  # window / frame background
    surface: str  # inputs, table background
    zebra: str  # alternate row background
    border: str  # entry border / separators
    # Text
    fg: str  # primary text
    muted: str  # secondary text (stats, footer, ids)
    # Single action accent (same hue family in both themes)
    action: str  # primary button bg
    action_fg: str  # text on top of action
    action_active: str  # pressed/hover approximation
    # Status (text only, never big blocks)
    ok: str
    err: str
    # Selection
    select_bg: str
    select_fg: str
    #Done rows
    done_fg: str


LIGHT = Theme(
    name="light",
    label="Claro",
    bg="#FFFFFF",
    surface="#EDF1F6",
    zebra="#F7F9FC",
    border="#D5DCE6",
    fg="#1A2333",
    muted="#5B6B82",
    action="#2B5CE6",
    action_fg="#FFFFFF",
    action_active="#1E46B8",
    ok="#1E9E6A",
    err="#C43D2B",
    select_bg="#2B5CE6",
    select_fg="#FFFFFF",
    done_fg="#5B6B82",
)

DARK = Theme(
    name="dark",
    label="Escuro",
    bg="#151D2A",
    surface="#1F2A3C",
    zebra="#1A2434",
    border="#2E3B51",
    fg="#E8EDF4",
    muted="#93A1B8",
    action="#7A9BFF",
    action_fg="#101828",
    action_active="#9DB6FF",
    ok="#4CC38A",
    err="#F0725C",
    select_bg="#7A9BFF",
    select_fg="#101828",
    done_fg="#93A1B8",
)

THEMES: dict[str, Theme] = {"light": LIGHT, "dark": DARK}

THEME_FILE = Path.home() / ".config" / "taskforce" / "theme.json"


def load_theme_name() -> str:
    """Resolution order: env TASKFORCE_THEME > theme.json > 'light'."""
    raw = (os.getenv("TASKFORCE_THEME") or "").strip().lower()
    if raw in THEMES:
        return raw
    try:
        data = json.loads(THEME_FILE.read_text(encoding="utf-8"))
        name = str(data.get("theme", "")).strip().lower()
        if name in THEMES:
            return name
    except (OSError, ValueError):
        pass
    return "light"


def save_theme_name(name: str) -> None:
    """Persist the toggle choice; failures are silent (theme is cosmetic)."""
    if name not in THEMES:
        return
    try:
        THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
        THEME_FILE.write_text(json.dumps({"theme": name}), encoding="utf-8")
    except OSError:
        pass
