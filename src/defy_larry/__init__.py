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
from larry.plugins import apply_plugin_filter
from serial.tools.list_ports import comports

from defy_larry.keyboard import Keyboard


def plugin(colors: ColorList, config: ConfigType) -> None:
    """Dygma Defy plugin"""
    for device in [p.device for p in comports() if p.manufacturer == "DYGMA"]:
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
        colors = (
            list(Color.generate_from(colors, palette_size))
            if len(colors) <= palette_size
            else Color.dominant(colors, palette_size)
        )
        colors = apply_plugin_filter(colors, config)
        for index, color in get_overrides(config):
            colors[index] = color
        kb.set_palette(colors)


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
