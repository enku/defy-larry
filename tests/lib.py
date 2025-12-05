# pylint: disable=missing-docstring,redefined-outer-name
import configparser
import random as _random
from typing import Sequence
from unittest import mock

import larry.color
import numpy as np
import serial
from larry.config import ConfigType
from unittest_fixtures import FixtureContext, Fixtures, fixture

import defy_larry
from defy_larry import keyboard as kb

Mock = mock.Mock


@fixture()
def serial_class(_: Fixtures) -> FixtureContext[Mock]:
    """Mock serial.Serial class"""
    with mock.patch.object(serial, "Serial", autospec=True, create=False) as mock_obj:
        yield mock_obj


@fixture(serial_class)
def serial_device(fixtures: Fixtures, port: str = "/dev/ttyACM0") -> Mock:
    """Mock serial.Serial device"""
    return fixtures.serial_class(
        port, baudrate=kb.BAUD_RATE, timeout=kb.TIMEOUT, write_timeout=kb.TIMEOUT
    )


@fixture(serial_device)
def keyboard(fixtures: Fixtures) -> kb.Keyboard:
    """Keyboard instance with mock serial_device"""
    return kb.Keyboard(fixtures.serial_device)


@fixture()
def keyboard_open(_: Fixtures) -> FixtureContext[Mock]:
    with mock.patch.object(kb.Keyboard, "open") as mock_obj:
        yield mock_obj


@fixture()
def random(_: Fixtures, seed: int = 1) -> FixtureContext[None]:
    with mock.patch.object(larry.color, "random", _random.Random(seed)):
        np.random.rand(seed)
        yield


@fixture()
def comports(
    _: Fixtures, devices: Sequence[str] = ("/dev/null",)
) -> FixtureContext[Mock]:
    with mock.patch.object(defy_larry, "comports") as mock_obj:
        mock_obj.return_value = [
            mock.Mock(manufacturer="DYGMA", device=device) for device in devices
        ]
        yield mock_obj


@fixture()
def colorize_keyboard(_: Fixtures) -> FixtureContext[Mock]:
    with mock.patch.object(defy_larry, "colorize_keyboard") as mock_obj:
        yield mock_obj


@fixture()
def colors(
    _: Fixtures, colors: str = "#a916e2 #ffc0cb #e2bd16"
) -> list[larry.color.Color]:
    return make_colors(*colors.split())


def make_colors(*color_str: str) -> larry.color.ColorList:
    return [larry.color.Color(s) for s in color_str]


def make_config(**options: str) -> ConfigType:
    parser = configparser.ConfigParser()
    parser.add_section("defy_larry")
    config = ConfigType(parser, name="defy_larry")

    for name, value in options.items():
        config[name] = value

    return config


def make_palette_str(colors: Sequence[larry.color.Color]) -> bytes:
    cstr = " ".join(f"{r} {g} {b} {w}" for c in colors for r, g, b, w in [c.to_rgbw()])

    return cstr.encode("ascii") + b"\r\n"
