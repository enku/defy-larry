# pylint: disable=missing-docstring
import io
import random
from contextlib import redirect_stderr
from unittest import TestCase, mock

import numpy as np
import serial
from larry.color import Color

from defy_larry import errmsg, maybe_colorize_keyboard, plugin

from . import make_colors, make_config


@mock.patch("larry.color.random", random.Random(1))
@mock.patch("defy_larry.comports")
@mock.patch("defy_larry.Keyboard.open")
class PluginTests(TestCase):
    def setUp(self) -> None:
        super().setUp()

        np.random.rand(1)

    def test(self, keyboard_open: mock.Mock, comports: mock.Mock) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config()
        comports.return_value = [mock.Mock(manufacturer="DYGMA", device="/dev/null")]

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

    def test_override_option(
        self, keyboard_open: mock.Mock, comports: mock.Mock
    ) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config(override="2=000000")
        comports.return_value = [mock.Mock(manufacturer="DYGMA", device="/dev/null")]

        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        plugin(colors, config)

        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(
                    [Color("#db7fff"), Color("#ff7f95"), Color("#000000")]
                ),
            ]
        )

    def test_soften_effect(self, keyboard_open: mock.Mock, comports: mock.Mock) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config(effect="soften")
        comports.return_value = [mock.Mock(manufacturer="DYGMA", device="/dev/null")]

        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(
                    [Color("#d283f0"), Color("#ffdfe4"), Color("#f0dc83")]
                ),
            ]
        )

    def test_luminize_effect(
        self, keyboard_open: mock.Mock, comports: mock.Mock
    ) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config(effect="luminize")
        comports.return_value = [mock.Mock(manufacturer="DYGMA", device="/dev/null")]

        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(
                    [Color("#d7a2ab"), Color("#deb916"), Color("#ff2cff")]
                ),
            ]
        )

    def test_serial_exception(
        self, keyboard_open: mock.Mock, comports: mock.Mock
    ) -> None:
        colors = make_colors("red", "pink", "blue")
        config = make_config()
        comports.return_value = [mock.Mock(manufacturer="DYGMA", device="/dev/null")]
        keyboard_open.side_effect = serial.SerialException("oh no!")
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            plugin(colors, config)

        self.assertEqual(
            "An occurred while attempting to colorize the /dev/null keyboard:\noh no!\n",
            stderr.getvalue(),
        )

    def test_multiple_devices(
        self, keyboard_open: mock.Mock, comports: mock.Mock
    ) -> None:
        colors = make_colors("red", "pink", "blue")
        config = make_config()
        comports.return_value = [
            mock.Mock(manufacturer="DYGMA", device="/dev/foo"),
            mock.Mock(manufacturer="DYGMA", device="/dev/bar"),
        ]
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]

        plugin(colors, config)

        self.assertEqual(keyboard_open.call_count, 2)


@mock.patch("defy_larry.colorize_keyboard")
class MaybeColorizeKeyboardTests(TestCase):
    def test(self, colorize_keyboard: mock.Mock) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config()

        is_colorized = maybe_colorize_keyboard("/dev/null", colors, config)

        self.assertIs(True, is_colorized)

        colorize_keyboard.side_effect = serial.SerialException("oops!")
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            is_colorized = maybe_colorize_keyboard("/dev/null", colors, config)

        self.assertIs(False, is_colorized)
        self.assertEqual(
            "An occurred while attempting to colorize the /dev/null keyboard:\noops!\n",
            stderr.getvalue(),
        )


class ErrmsgTests(TestCase):
    def test(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            errmsg("This is a test")

        self.assertEqual("This is a test\n", stderr.getvalue())
