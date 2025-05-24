# pylint: disable=missing-docstring
import io
import random
from contextlib import redirect_stderr
from unittest import TestCase, mock

import serial
from larry.color import Color

from defy_larry import errmsg, plugin

from . import make_colors, make_config


@mock.patch("larry.color.random", random.Random(1))
@mock.patch("defy_larry.Keyboard.open")
class PluginTests(TestCase):
    def test(self, keyboard_open: mock.Mock) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config()

        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(
                    [Color("#ffe77f"), Color("#ff7f95"), Color("#db7fff")]
                ),
            ]
        )

    def test_soften_effect(self, keyboard_open: mock.Mock) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config(effect="soften")

        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(
                    [Color("#ffdfe4"), Color("#f0dc83"), Color("#d283f0")]
                ),
            ]
        )

    def test_serial_exception(self, keyboard_open: mock.Mock) -> None:
        colors = make_colors("red", "pink", "blue")
        config = make_config()
        keyboard_open.side_effect = serial.SerialException("oh no!")
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            plugin(colors, config)

        self.assertEqual(
            "An occurred while attempting to colorize the /dev/null keyboard:\noh no!\n",
            stderr.getvalue(),
        )

    def test_multiple_devices(self, keyboard_open: mock.Mock) -> None:
        colors = make_colors("red", "pink", "blue")
        config = make_config(["/dev/foo", "/dev/bar"])
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]

        plugin(colors, config)

        self.assertEqual(keyboard_open.call_count, 2)


class ErrmsgTests(TestCase):
    def test(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            errmsg("This is a test")

        self.assertEqual("This is a test\n", stderr.getvalue())
