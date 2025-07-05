# pylint: disable=missing-docstring
import configparser
from typing import Sequence

from larry.color import Color, ColorList
from larry.config import ConfigType


def make_colors(*color_str: str) -> ColorList:
    return [Color(s) for s in color_str]


def make_config(effect: str = "pastelize", override: str = "") -> ConfigType:
    parser = configparser.ConfigParser()
    parser.add_section("defy_larry")
    config = ConfigType(parser, name="defy_larry")
    config["effect"] = effect

    if override:
        config["override"] = override

    return config


def make_palette_str(colors: Sequence[Color]) -> bytes:
    cstr = " ".join(f"{r} {g} {b} {w}" for c in colors for r, g, b, w in [c.to_rgbw()])

    return cstr.encode("ascii") + b"\r\n"
