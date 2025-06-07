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

# Value to use for the "luminize" effect. This should probably be made an option at some
# point. I'm waiting until I move "enhance" into larry proper.
LUMINANCE = 178.5


def plugin(colors: ColorList, config: ConfigType) -> None:
    """Dygma Defy plugin"""
    device_str = config.get("devices", fallback="") or "/dev/ttyACM0"

    for device in device_str.strip().split():
        maybe_colorize_keyboard(device, colors, config)


def maybe_colorize_keyboard(device: str, colors: ColorList, config: ConfigType) -> bool:
    """Colorize the keyboard at the given device using the given source colors

    Return True.

    If a SerialException occurs, write the message to stderr and return False
    """
    try:
        colorize_keyboard(device, colors, config)
        return True
    except serial.SerialException as error:
        errmsg(f"An occurred while attempting to colorize the {device} keyboard:")
        errmsg(f"{error}")
        return False


def colorize_keyboard(device: str, colors: ColorList, config: ConfigType) -> None:
    """Colorize the keyboard at the given device using the given source colors"""
    with Keyboard.open(device) as kb:
        palette = kb.get_palette()
        palette_size = len(palette)
        intensity = config.getfloat("intensity", fallback=0.0)
        colors = (
            list(Color.generate_from(colors, palette_size))
            if len(colors) <= palette_size
            else Color.dominant(colors, palette_size)
        )
        colors = [enhance(c, config).intensify(intensity) for c in colors]
        for index, color in get_overrides(config):
            colors[index] = color
        kb.set_palette(colors)


def enhance(color: Color, config: ConfigType, default: str = "none") -> Color:
    """Maybe enhance color based on config"""
    effect = config.get("effect", fallback=default)

    match effect:
        case "pastelize":
            color = color.pastelize()
        case "soften":
            color = color.soften()
        case "luminize":
            color = color.luminize(LUMINANCE)

    return color


def get_overrides(config: ConfigType) -> list[tuple[int, Color]]:
    """Given the config return a list of (index, Color) palette overrides"""
    overrides = []

    for item in (config.get("override") or "").strip().split():
        parts = item.partition("=")

        if all(parts):
            overrides.append((int(parts[0]), Color(parts[2])))

    return overrides


def errmsg(message: str) -> None:
    """Print the given message to stderr"""
    print(message, file=sys.stderr)
