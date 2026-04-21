# Catppuccin Mocha
C = {
    "base":     "#1e1e2e",
    "mantle":   "#181825",
    "crust":    "#11111b",
    "surface0": "#313244",
    "surface1": "#45475a",
    "surface2": "#585b70",
    "overlay0": "#6c7086",
    "overlay1": "#7f849c",
    "text":     "#cdd6f4",
    "subtext0": "#a6adc8",
    "subtext1": "#bac2de",
    "blue":     "#89b4fa",
    "lavender": "#b4befe",
    "sapphire": "#74c7ec",
    "teal":     "#94e2d5",
    "green":    "#a6e3a1",
    "yellow":   "#f9e2af",
    "peach":    "#fab387",
    "maroon":   "#eba0ac",
    "red":      "#f38ba8",
    "mauve":    "#cba6f7",
    "pink":     "#f5c2e7",
}

TAG_COLORS = [
    C["blue"], C["mauve"], C["teal"], C["peach"],
    C["green"], C["yellow"], C["sapphire"], C["pink"],
    C["lavender"], C["maroon"],
]


def tag_color(tags: list[str], tag: str) -> str:
    try:
        return TAG_COLORS[tags.index(tag) % len(TAG_COLORS)]
    except ValueError:
        return TAG_COLORS[0]
