AVAILABLE_BORDERS = [
    "single",
    "single-thick",
    "single-rounded",
    "double",
    "pipe-joints"
]

# symbol sets, depending on table border style
border_symbols = {
    "single": {
        "TOP_LEFT": u"\u250C",
        "TOP_RIGHT": u"\u2510",
        "BOTTOM_LEFT": u"\u2514",
        "BOTTOM_RIGHT": u"\u2518",
        "TOP_TEE": u"\u252C",
        "BOTTOM_TEE": u"\u2534",
        "LEFT_TEE": u"\u251C",
        "RIGHT_TEE": u"\u2524",
        "INTERSECT": u"\u253C",

        "VBAR": u"\u2502",
        "HBAR": u"\u2500",
    },
    "single-thick": {
        "TOP_LEFT": u"\u250F",
        "TOP_RIGHT": u"\u2513",
        "BOTTOM_LEFT": u"\u2517",
        "BOTTOM_RIGHT": u"\u251B",
        "TOP_TEE": u"\u2533",
        "BOTTOM_TEE": u"\u253B",
        "LEFT_TEE": u"\u2523",
        "RIGHT_TEE": u"\u252B",
        "INTERSECT": u"\u254B",

        "VBAR": u"\u2503",
        "HBAR": u"\u2501",
    },
    "single-rounded": {
        "TOP_LEFT": u"\u256D",
        "TOP_RIGHT": u"\u256E",
        "BOTTOM_LEFT": u"\u2570",
        "BOTTOM_RIGHT": u"\u256F",
        "TOP_TEE": u"\u252C",
        "BOTTOM_TEE": u"\u2534",
        "LEFT_TEE": u"\u251C",
        "RIGHT_TEE": u"\u2524",
        "INTERSECT": u"\u253C",

        "VBAR": u"\u2502",
        "HBAR": u"\u2500",
    },
    "double": {
        "TOP_LEFT": u"\u2554",
        "TOP_RIGHT": u"\u2557",
        "BOTTOM_LEFT": u"\u255A",
        "BOTTOM_RIGHT": u"\u255D",
        "TOP_TEE": u"\u2566",
        "BOTTOM_TEE": u"\u2569",
        "LEFT_TEE": u"\u2560",
        "RIGHT_TEE": u"\u2563",
        "INTERSECT": u"\u256C",

        "VBAR": u"\u2551",
        "HBAR": u"\u2550",
    },
    "pipe-joints": {
        "TOP_LEFT": u"\u250F",
        "TOP_RIGHT": u"\u2513",
        "BOTTOM_LEFT": u"\u2517",
        "BOTTOM_RIGHT": u"\u251B",
        "TOP_TEE": u"\u2533",
        "BOTTOM_TEE": u"\u253B",
        "LEFT_TEE": u"\u2523",
        "RIGHT_TEE": u"\u252B",
        "INTERSECT": u"\u254B",

        "VBAR": u"\u2502",
        "HBAR": u"\u2500",
    },
}
