from unittest import TestCase
from unittest.mock import patch
import bme280

class SpiDevMock:
    def open(self, bus, cs):
        assert bus == 42 and cs == 2

    def close(self):
        pass

    def xfer2(self, data):
        length = len(data)
        assert length >= 1
        reg = data[0]
        if reg == 0xD0 and length == 1 + 1: # id
            return b'\0' + bytes([ 0x60, ])
        if reg == 0x88 and length == 26 + 1: # cal burst 1
            return b'\0' + bytes([ 0x01, ] * (length - 1))
        if reg == 0xE1 and length == 7 + 1: # cal burst 2
            return b'\0' + bytes([ 0x01, ] * (length - 1))
        if reg == 0xF7 and length == 8 + 1: # value burst
            return b'\0' + bytes([ 0x01, 0x02, 0x03,  # press
                                   0x74, 0x75, 0x76,  # temp
                                   0x18, 0x18, ])     # hum
        return bytes([ 0, ] * length)

class Test_SPIDummy(TestCase):
    @patch("spidev.SpiDev", SpiDevMock)
    def test_linux(self):
        with bme280.BME280(spiBus=42, spiCS=2) as bme:
            t, h, p = bme.readForced(filter=bme280.FILTER_4,
                                     tempOversampling=bme280.OVSMPL_4,
                                     humidityOversampling=bme280.OVSMPL_16,
                                     pressureOversampling=bme280.OVSMPL_4)
            #TODO

# vim: ts=4 sw=4 expandtab
