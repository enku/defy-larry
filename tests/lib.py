# pylint: disable=missing-docstring
import random as _random
from typing import Sequence
from unittest import mock

import larry.color
import numpy as np
import serial
from unittest_fixtures import FixtureContext, Fixtures, fixture

import defy_larry
from defy_larry import keyboard as kb

FC = FixtureContext
Mock = mock.Mock


@fixture()
def serial_class(_: Fixtures) -> FC[Mock]:
    """Mock serial.Serial class"""
    with mock.patch.object(serial, "Serial", autospec=True, create=False) as mock_obj:
        yield mock_obj


@fixture(serial_class)
def serial_device(fixtures: Fixtures, port: str = "/dev/ttyACM0") -> Mock:
    """Mock serial.Serial device"""
    return fixtures.serial_class(
        port, baudrate=kb.BAUD_RATE, timeout=kb.TIMEOUT, write_timeout=kb.TIMEOUT
    )


@fixture()
def keyboard_open(_: Fixtures) -> FC[Mock]:
    with mock.patch.object(kb.Keyboard, "open") as mock_obj:
        yield mock_obj


@fixture()
def random(_: Fixtures, seed: int = 1) -> FC[None]:
    with mock.patch.object(larry.color, "random", _random.Random(seed)):
        np.random.rand(seed)
        yield


@fixture()
def comports(_: Fixtures, devices: Sequence[str] = ("/dev/null",)) -> FC[Mock]:
    with mock.patch.object(defy_larry, "comports") as mock_obj:
        mock_obj.return_value = [
            mock.Mock(manufacturer="DYGMA", device=device) for device in devices
        ]
        yield mock_obj
