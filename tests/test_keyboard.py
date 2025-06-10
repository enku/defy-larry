# pylint: disable=missing-docstring
from unittest import TestCase, mock

import serial
from larry.color import Color

from defy_larry import keyboard


class InitializerTests(TestCase):
    def test(self) -> None:
        serial_device = mock.Mock(spec=serial.Serial)()

        kb = keyboard.Keyboard(serial_device)

        self.assertEqual(kb.serial_device, serial_device)


class GetPaletteTests(TestCase):
    def test(self):
        serial_device = mock.Mock(spec=serial.Serial)()
        kb = keyboard.Keyboard(serial_device)
        palette_str = (
            b"0 126 128 127 0 31 128 127 99 128 0 127 0 44 128 127 61 128 0 127"
            b" 0 128 38 127 128 68 0 127 128 0 53 127 0 48 128 127 22 128 0 127"
            b" 0 73 128 127 96 0 128 127 128 78 0 127 128 81 0 127 56 128 0 127"
            b" 128 15 0 127 \r\n"
        )
        serial_device.readline.return_value = palette_str

        colors = kb.get_palette()

        expected = [
            Color(127, 253, 255),
            Color(127, 158, 255),
            Color(226, 255, 127),
            Color(127, 171, 255),
            Color(188, 255, 127),
            Color(127, 255, 165),
            Color(255, 195, 127),
            Color(255, 127, 180),
            Color(127, 175, 255),
            Color(149, 255, 127),
            Color(127, 200, 255),
            Color(223, 127, 255),
            Color(255, 205, 127),
            Color(255, 208, 127),
            Color(183, 255, 127),
            Color(255, 142, 127),
        ]
        self.assertEqual(expected, colors)

        serial_device.write.assert_called_once_with(b"palette\n")


class SetPaletteTests(TestCase):
    def test(self) -> None:
        serial_device = mock.Mock(spec=serial.Serial)()
        kb = keyboard.Keyboard(serial_device)
        colors = [
            Color(127, 253, 255),
            Color(127, 158, 255),
            Color(226, 255, 127),
            Color(127, 171, 255),
            Color(188, 255, 127),
            Color(127, 255, 165),
            Color(255, 195, 127),
            Color(255, 127, 180),
            Color(127, 175, 255),
            Color(149, 255, 127),
            Color(127, 200, 255),
            Color(223, 127, 255),
            Color(255, 205, 127),
            Color(255, 208, 127),
            Color(183, 255, 127),
            Color(255, 142, 127),
        ]

        kb.set_palette(colors)

        expected = (
            b"palette"
            b" 0 126 128 127 0 31 128 127 99 128 0 127 0 44 128 127 61 128 0 127"
            b" 0 128 38 127 128 68 0 127 128 0 53 127 0 48 128 127 22 128 0 127 0"
            b" 73 128 127 96 0 128 127 128 78 0 127 128 81 0 127 56 128 0 127"
            b" 128 15 0 127\n"
        )
        serial_device.write.assert_called_once_with(expected)

    def test_empty_color_list(self) -> None:
        serial_device = mock.Mock(spec=serial.Serial)()
        kb = keyboard.Keyboard(serial_device)

        kb.set_palette([])

        serial_device.write.assert_not_called()


@mock.patch.object(keyboard.serial, "Serial", spec=serial.Serial)
class OpenTests(TestCase):
    def test(self, serial_class: mock.Mock):
        port = "/dev/null"

        with keyboard.Keyboard.open(port) as kb:
            self.assertIsInstance(kb, keyboard.Keyboard)
            serial_class.assert_called_once_with(
                port, baudrate=keyboard.BAUD_RATE, timeout=keyboard.TIMEOUT
            )
            serial_device = serial_class.return_value
            self.assertEqual(kb.serial_device, serial_device)
            serial_device.close.assert_not_called()

        serial_device.close.assert_called_once_with()
