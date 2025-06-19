# pylint: disable=missing-docstring
import configparser

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
