# pylint: disable=missing-docstring
import io
from contextlib import redirect_stderr
from unittest import IsolatedAsyncioTestCase, TestCase, mock

import serial
from larry.color import Color
from unittest_fixtures import Fixtures, given

from defy_larry import errmsg, maybe_colorize_keyboard, plugin

from . import lib


@given(lib.keyboard_open, lib.random, lib.comports, lib.colors)
class PluginTests(IsolatedAsyncioTestCase):
    async def test(self, fixtures: Fixtures) -> None:
        colors = fixtures.colors
        config = lib.make_config()

        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        await plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(lib.make_colors("#e2bd16", "#ffc0cb", "#a916e2")),
            ]
        )

    async def test_override_option(self, fixtures: Fixtures) -> None:
        colors = fixtures.colors
        config = lib.make_config(override="2=000000")

        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        await plugin(colors, config)

        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(lib.make_colors("#e2bd16", "#ffc0cb", "#000000")),
            ]
        )

    async def test_soften_effect(self, fixtures: Fixtures) -> None:
        colors = fixtures.colors
        config = lib.make_config(filter="soften")

        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        await plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(lib.make_colors("#f0dc83", "#ffdfe4", "#d283f0")),
            ]
        )

    async def test_luminize_effect(self, fixtures: Fixtures) -> None:
        colors = fixtures.colors
        config = lib.make_config(filter="luminize")

        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]
        await plugin(colors, config)

        keyboard_open.assert_called_once_with("/dev/null")
        kb.assert_has_calls(
            [
                mock.call.get_palette(),
                mock.call.set_palette(lib.make_colors("#deb916", "#d7a2ab", "#ff2cff")),
            ]
        )

    async def test_serial_exception(self, fixtures: Fixtures) -> None:
        colors = fixtures.colors
        config = lib.make_config()
        keyboard_open = fixtures.keyboard_open
        keyboard_open.side_effect = serial.SerialException("oh no!")
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            await plugin(colors, config)

        self.assertEqual(
            "An occurred while attempting to colorize the /dev/null keyboard:\noh no!\n",
            stderr.getvalue(),
        )

    async def test_multiple_devices(self, fixtures: Fixtures) -> None:
        colors = fixtures.colors
        config = lib.make_config()
        fixtures.comports.return_value = [
            mock.Mock(manufacturer="DYGMA", device="/dev/foo"),
            mock.Mock(manufacturer="DYGMA", device="/dev/bar"),
        ]
        keyboard_open = fixtures.keyboard_open
        kb = keyboard_open.return_value.__enter__.return_value
        kb.get_palette.return_value = [Color() for _ in range(3)]

        await plugin(colors, config)

        self.assertEqual(keyboard_open.call_count, 2)


@given(lib.colorize_keyboard, lib.colors)
class MaybeColorizeKeyboardTests(IsolatedAsyncioTestCase):
    async def test_colorizes(self, fixtures: Fixtures) -> None:
        colors = fixtures.colors
        config = lib.make_config()

        is_colorized = await maybe_colorize_keyboard("/dev/null", colors, config)

        self.assertIs(True, is_colorized)
        fixtures.colorize_keyboard.assert_called_once_with("/dev/null", colors, config)

    async def test_with_exception(self, fixtures: Fixtures) -> None:
        colors = fixtures.colors
        config = lib.make_config()
        colorize_keyboard = fixtures.colorize_keyboard
        colorize_keyboard.side_effect = serial.SerialException("oops!")
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            is_colorized = await maybe_colorize_keyboard("/dev/null", colors, config)

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
