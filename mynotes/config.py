# Catppuccin Mocha-inspired dark palette — all UI colors come from here.
C = {
    "base":     "#171a2e",   # main window background
    "mantle":   "#11142a",   # sidebar and topbar
    "crust":    "#0b0d1f",
    "surface0": "#252842",   # card and input background
    "surface1": "#363a54",
    "surface2": "#464b65",
    "overlay0": "#6b6f8a",
    "overlay1": "#7f849c",
    "text":     "#cdd6f4",
    "subtext0": "#a6adc8",
    "subtext1": "#bac2de",
    "blue":     "#89b4fa",
    "lavender": "#b4befe",
    "sapphire": "#74c7ec",
    "sky":      "#89dceb",
    "teal":     "#94e2d5",
    "green":    "#a6e3a1",
    "yellow":   "#f9e2af",
    "peach":    "#fab387",
    "flamingo": "#f2cdcd",
    "maroon":   "#eba0ac",
    "red":      "#f38ba8",
    "mauve":    "#cba6f7",
    "pink":     "#f5c2e7",
    "rosewater":"#f5e0dc",
}

# Cycles through these accent colors when assigning a color to each tag.
TAG_COLORS = [
    C["blue"], C["mauve"], C["teal"], C["peach"],
    C["green"], C["yellow"], C["sapphire"], C["pink"],
    C["lavender"], C["maroon"], C["sky"], C["flamingo"],
]

# Per-note color presets. `bg` overrides the card background; `accent` overrides
# the top stripe and hover border. None means "use tag color / default surface".
NOTE_COLORS: dict[str, dict] = {
    "default":   {"bg": None,        "accent": None},
    "red":       {"bg": "#3b1e28",   "accent": "#f38ba8"},
    "flamingo":  {"bg": "#3b2228",   "accent": "#f2cdcd"},
    "peach":     {"bg": "#3b2718",   "accent": "#fab387"},
    "yellow":    {"bg": "#38371a",   "accent": "#f9e2af"},
    "green":     {"bg": "#1a3328",   "accent": "#a6e3a1"},
    "teal":      {"bg": "#1a3235",   "accent": "#94e2d5"},
    "sky":       {"bg": "#1a2f38",   "accent": "#89dceb"},
    "sapphire":  {"bg": "#182838",   "accent": "#74c7ec"},
    "blue":      {"bg": "#1a2840",   "accent": "#89b4fa"},
    "lavender":  {"bg": "#1f2040",   "accent": "#b4befe"},
    "mauve":     {"bg": "#2a1e3b",   "accent": "#cba6f7"},
    "pink":      {"bg": "#3b1a35",   "accent": "#f5c2e7"},
    "rosewater": {"bg": "#3b1f2a",   "accent": "#f5e0dc"},
}


def tag_color(tags: list[str], tag: str) -> str:
    # Derives a stable accent color for a tag by cycling through TAG_COLORS
    # based on the tag's position in the list.
    try:
        return TAG_COLORS[tags.index(tag) % len(TAG_COLORS)]
    except ValueError:
        return TAG_COLORS[0]
