from ._types import COLOR

__all__ = [
    "WHITE",
    "ORANGE",
    "MAGENTA",
    "LIGHT_BLUE",
    "YELLOW",
    "LIME",
    "PINK",
    "GRAY",
    "LIGHT_GRAY",
    "CYAN",
    "PURPLE",
    "BLUE",
    "BROWN",
    "GREEN",
    "RED",
    "BLACK",
    # Deutsche Konstanten
    "WEISS",
    "HELLBLAU",
    "GELB",
    "LINDGRÜN",
    "ROSA",
    "GRAU",
    "HELLGRAU",
    "TÜRKIS",
    "VIOLETT",
    "BLAU",
    "BRAUN",
    "GRÜN",
    "ROT",
    "SCHWARZ",
]

color_codes: dict[COLOR, int] = {
    "white": 0xF9FFFE,
    "orange": 0xF9801D,
    "magenta": 0xC74EBD,
    "light_blue": 0x3AB3DA,
    "yellow": 0xFED83D,
    "lime": 0x80C71F,
    "pink": 0xF38BAA,
    "gray": 0x474F52,
    "light_gray": 0x9D9D97,
    "cyan": 0x169C9C,
    "purple": 0x8932B8,
    "blue": 0x3C44AA,
    "brown": 0x835432,
    "green": 0x5E7C16,
    "red": 0xB02E26,
    "black": 0x1D1D21,
}

WHITE = "white"
ORANGE = "orange"
MAGENTA = "magenta"
LIGHT_BLUE = "light_blue"
YELLOW = "yellow"
LIME = "lime"
PINK = "pink"
GRAY = "gray"
LIGHT_GRAY = "light_gray"
CYAN = "cyan"
PURPLE = "purple"
BLUE = "blue"
BROWN = "brown"
GREEN = "green"
RED = "red"
BLACK = "black"

# Deutsche Bezeichnungen

WEISS = WHITE
# ORANGE = ORANGE
# MAGENTA = MAGENTA
HELLBLAU = LIGHT_BLUE
GELB = YELLOW
LINDGRÜN = LIME
ROSA = PINK
GRAU = GRAY
HELLGRAU = LIGHT_GRAY
TÜRKIS = CYAN
VIOLETT = PURPLE
BLAU = BLUE
BRAUN = BROWN
GRÜN = GREEN
ROT = RED
SCHWARZ = BLACK
