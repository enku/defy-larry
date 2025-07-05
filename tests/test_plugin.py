# pylint: disable=missing-docstring
import io
from contextlib import redirect_stderr
from unittest import TestCase, mock

import serial
from larry.color import Color
from unittest_fixtures import Fixtures, given

from defy_larry import errmsg, maybe_colorize_keyboard, plugin

from . import lib, make_colors, make_config


@given(lib.keyboard_open, lib.random, lib.comports)
class PluginTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config()

        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(make_colors("#ffe77f", "#ff7f95", "#db7fff")),
            ]
        )

    def test_override_option(self, fixtures: Fixtures) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config(override="2=000000")

        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        plugin(colors, config)

        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(make_colors("#ffe77f", "#ff7f95", "#000000")),
            ]
        )

    def test_soften_effect(self, fixtures: Fixtures) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config(effect="soften")

        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(make_colors("#f0dc83", "#ffdfe4", "#d283f0")),
            ]
        )

    def test_luminize_effect(self, fixtures: Fixtures) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config(effect="luminize")

        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(make_colors("#deb916", "#d7a2ab", "#ff2cff")),
            ]
        )

    def test_serial_exception(self, fixtures: Fixtures) -> None:
        colors = make_colors("red", "pink", "blue")
        config = make_config()
        keyboard_open = fixtures.keyboard_open
        keyboard_open.side_effect = serial.SerialException("oh no!")
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            plugin(colors, config)

        self.assertEqual(
            "An occurred while attempting to colorize the /dev/null keyboard:\noh no!\n",
            stderr.getvalue(),
        )

    def test_multiple_devices(self, fixtures: Fixtures) -> None:
        colors = make_colors("red", "pink", "blue")
        config = make_config()
        fixtures.comports.return_value = [
            mock.Mock(manufacturer="DYGMA", device="/dev/foo"),
            mock.Mock(manufacturer="DYGMA", device="/dev/bar"),
        ]
        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]

        plugin(colors, config)

        self.assertEqual(keyboard_open.call_count, 2)


@given(lib.colorize_keyboard)
class MaybeColorizeKeyboardTests(TestCase):
    def test_colorizes(self, fixtures: Fixtures) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config()

        is_colorized = maybe_colorize_keyboard("/dev/null", colors, config)

        self.assertIs(True, is_colorized)
        fixtures.colorize_keyboard.assert_called_once_with("/dev/null", colors, config)

    def test_with_exception(self, fixtures: Fixtures) -> None:
        colors = make_colors("#a916e2", "#ffc0cb", "#e2bd16")
        config = make_config()
        colorize_keyboard = fixtures.colorize_keyboard
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
