from unittest import TestCase
from unittest.mock import patch
import bme280

class SMBusMock:
    def __init__(self, bus):
        assert bus == 42

    def close(self):
        pass

    def write_i2c_block_data(self, addr, reg, data):
        pass

    def read_i2c_block_data(self, addr, reg, length):
        if reg == 0xD0 and length == 1: # id
            return [ 0x60, ]
        if reg == 0x88 and length == 26: # cal burst 1
            return [ 0x01, ] * length
        if reg == 0xE1 and length == 7: # cal burst 2
            return [ 0x01, ] * length
        if reg == 0xF7 and length == 8: # value burst
            return [ 0x01, 0x02, 0x03,  # press
                     0x74, 0x75, 0x76,  # temp
                     0x18, 0x18, ]      # hum
        return [ 0, ] * length

class Test_I2CDummy(TestCase):
    @patch("smbus.SMBus", SMBusMock)
    def test_linux(self):
        with bme280.BME280(i2cBus=42) as bme:
            t, h, p = bme.readForced(filter=bme280.FILTER_4,
                                     tempOversampling=bme280.OVSMPL_4,
                                     humidityOversampling=bme280.OVSMPL_16,
                                     pressureOversampling=bme280.OVSMPL_4)
            #TODO

# vim: ts=4 sw=4 expandtab
