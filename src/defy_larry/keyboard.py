"""Dygma Keyboard interface"""

from contextlib import contextmanager
from typing import Generator, Self

import serial
from larry.color import Color, ColorList

BAUD_RATE = 115200
ENCODING = "utf-8"
TIMEOUT = 5.0


class Keyboard:
    """Interface to the Dygma keyboard API"""

    def __init__(self, serial_device: serial.Serial) -> None:
        self.serial_device = serial_device

    def get_palette(self) -> ColorList:
        """Return the LED color pallete"""

        self.send("palette")
        response = self.receive()
        ints = [int(i) for i in response.strip().split()]

        return [
            Color.from_rgbw((ints[i], ints[i + 1], ints[i + 2], ints[i + 3]))
            for i in range(0, len(ints), 4)
        ]

    def set_palette(self, colors: ColorList) -> None:
        """Set the keyboard palette given the colors"""
        if colors:
            color_str = " ".join(str(i) for color in colors for i in color.to_rgbw())
            self.send(f"palette {color_str}")

    def send(self, command: str) -> None:
        """Send the given command to the keyboard"""
        serial_device = self.serial_device
        serial_device.write(f"{command}\r\n".encode(ENCODING))
        serial_device.flush()

    def receive(self) -> str:
        """Recieve a line from the keyboard"""
        serial_device = self.serial_device

        return serial_device.readline().decode(ENCODING).rstrip()

    @classmethod
    @contextmanager
    def open(cls, port: str) -> Generator[Self, None, None]:
        """Context manager to open the Keyboard interface.

        Closes the connection when the context ends.
        """
        device = serial.Serial(
            port, baudrate=BAUD_RATE, timeout=TIMEOUT, write_timeout=TIMEOUT
        )
        kb = cls(device)

        try:
            yield kb
        finally:
            device.close()
