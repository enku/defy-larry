r"""Defy Larry!

The Larry plugin for Digma Defy.

     _______
    < Defy! >
     -------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||
"""

import sys

import serial
from larry.color import Color, ColorList
from larry.config import ConfigType
from larry.utils import clip

from defy_larry.keyboard import Keyboard
from defy_larry.kmeans import get_centroids


def plugin(colors: ColorList, config: ConfigType) -> None:
    """Dygma Defy plugin"""
    device_str = config.get("devices", fallback="") or "/dev/ttyACM0"
    devices = device_str.strip().split()

    for device in devices:
        try:
            colorize_keyboard(device, colors, config)
        except serial.SerialException as error:
            print(
                f"An occurred while attempting to colorize the {device} keyboard:",
                file=sys.stderr,
            )
            print(f"{error}", file=sys.stderr)


def colorize_keyboard(device: str, colors: ColorList, config: ConfigType) -> None:
    """Colorize the keyboard at the given device using the given source colors"""
    with Keyboard.open(device) as kb:
        palette = kb.get_palette()
        palette_size = len(palette)
        intensity = config.getfloat("intensity", fallback=0.0)
        colors = (
            list(Color.generate_from(colors, palette_size))
            if len(colors) <= palette_size
            else dominant_colors(colors, palette_size)
        )
        kb.set_palette([enhance(c, config).intensify(intensity) for c in colors])


def dominant_colors(colors: ColorList, size: int) -> ColorList:
    """Return the size dominant colors from the ColorList"""
    return [Color(int(i[0]), int(i[1]), int(i[2])) for i in get_centroids(colors, size)]


def enhance(color: Color, config: ConfigType, default: str = "none") -> Color:
    """Maybe enhance color based on config"""
    effect = config.get("effect", fallback=default)

    match effect:
        case "pastelize":
            color = color.pastelize()
        case "soften":
            color = color.soften()

    return color
