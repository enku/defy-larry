# pylint: disable=missing-docstring
from unittest import mock

import serial
from unittest_fixtures import FixtureContext, Fixtures, fixture

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
