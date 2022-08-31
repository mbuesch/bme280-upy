#
# BME280 device driver
# Copyright (c) 2020-2022 Michael Büsch <m@bues.ch>
#
# The reference and base for this software is the public document
#   BME280 - Data sheet
#   Document revision         1.6
#   Document release date     September 2018
#   Technical reference code  0 273 141 185
#   Document number           BST-BME280-DS002-15
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__all__ = [
    "BME280Error",
    "BME280",
]

import sys

assert sys.version_info[0] == 3
isMicropython = sys.implementation.name == "micropython"

if isMicropython:
    import uasyncio as asyncio
    import micropython
    from micropython import const
else:
    import asyncio
    class micropython:
        const = native = viper = lambda x: x
    const = micropython.const

class BME280Error(Exception):
    """BME280 exception.
    """
    __slots__ = (
    )

def makePin(pin, constructor):
    from machine import Pin
    if isinstance(pin, Pin):
        return pin
    return constructor(pin)

class BME280I2C:
    """BME280 low level I2C wrapper.
    """
    __slots__ = (
        "__micropython",
        "__addr",
        "__i2c",
    )

    def __init__(self, i2cBus, i2cAddr, i2cFreq):
        self.__addr = i2cAddr
        self.__micropython = isMicropython
        try:
            if self.__micropython:
                from machine import I2C, SoftI2C, Pin
                if isinstance(i2cBus, (I2C, SoftI2C)):
                    self.__i2c = i2cBus
                else:
                    opts = {
                        "freq"  : i2cFreq * 1000,
                    }
                    if isinstance(i2cBus, dict):
                        opts["scl"] = makePin(i2cBus["scl"], lambda p: Pin(p, mode=Pin.OPEN_DRAIN, value=1))
                        opts["sda"] = makePin(i2cBus["sda"], lambda p: Pin(p, mode=Pin.OPEN_DRAIN, value=1))
                        i2cBus = i2cBus.get("index", -1)
                    else:
                        assert i2cBus >= 0
                    if i2cBus < 0:
                        self.__i2c = SoftI2C(**opts)
                    else:
                        self.__i2c = I2C(i2cBus, **opts)
            else:
                from smbus import SMBus
                if isinstance(i2cBus, SMBus):
                    self.__i2c = i2cBus
                else:
                    self.__i2c = SMBus(i2cBus)
        except Exception as e:
            raise BME280Error("BME280: I2C error: %s" % str(e))

    def close(self):
        if self.__micropython:
            try:
                if hasattr(self.__i2c, "deinit"):
                    self.__i2c.deinit()
            except Exception:
                pass
        else:
            try:
                self.__i2c.close()
            except Exception:
                pass
        self.__i2c = None

    def write(self, reg, data):
        try:
            if self.__micropython:
                self.__i2c.writeto_mem(self.__addr, reg, data)
            else:
                self.__i2c.write_i2c_block_data(self.__addr, reg, list(data))
        except Exception as e:
            raise BME280Error("BME280: I2C error: %s" % str(e))

    def read(self, reg, length):
        try:
            if self.__micropython:
                return self.__i2c.readfrom_mem(self.__addr, reg, length)
            else:
                return bytes(self.__i2c.read_i2c_block_data(self.__addr, reg, length))
        except Exception as e:
            raise BME280Error("BME280: I2C error: %s" % str(e))

class BME280SPI:
    """BME280 low level SPI wrapper.
    """
    __slots__ = (
        "__micropython",
        "__spi",
        "__cs",
    )

    def __init__(self, spiBus, spiCS, spiFreq):
        self.__micropython = isMicropython
        try:
            if self.__micropython:
                from machine import SPI, SoftSPI, Pin
                if spiCS is None:
                    raise Exception("No spiCS parameter specified.")
                if isinstance(spiBus, (SPI, SoftSPI)):
                    self.__spi = spiBus
                else:
                    opts = {
                        "baudrate"  : spiFreq * 1000,
                        "polarity"  : 0,
                        "phase"     : 0,
                        "bits"      : 8,
                        "firstbit"  : SPI.MSB,
                    }
                    if isinstance(spiBus, dict): # Software SPI
                        opts["sck"]  = makePin(spiBus["sck"], lambda p: Pin(p, mode=Pin.OUT, value=0))
                        opts["mosi"] = makePin(spiBus["mosi"], lambda p: Pin(p, mode=Pin.OUT, value=0))
                        opts["miso"] = makePin(spiBus["miso"], lambda p: Pin(p, mode=Pin.IN))
                        spiBus = spiBus.get("index", -1)
                    else:
                        assert spiBus >= 0
                    if spiBus < 0:
                        self.__spi = SoftSPI(**opts)
                    else:
                        self.__spi = SPI(spiBus, **opts)
                self.__cs = makePin(spiCS, lambda p: Pin(p, mode=Pin.OUT, value=1))
            else:
                from spidev import SpiDev
                if isinstance(spiBus, SpiDev):
                    self.__spi = spiBus
                else:
                    if spiCS is None:
                        raise Exception("No spiCS parameter specified.")
                    self.__spi = SpiDev()
                    self.__spi.max_speed_hz = spiFreq * 1000
                    self.__spi.mode = 0b00
                    self.__spi.bits_per_word = 8
                    self.__spi.threewire = False
                    self.__spi.lsbfirst = False
                    self.__spi.cshigh = False
                    self.__spi.open(spiBus, spiCS)
        except Exception as e:
            raise BME280Error("BME280: SPI error: %s" % str(e))

    def close(self):
        if self.__micropython:
            try:
                self.__cs(1)
            except Exception:
                pass
            try:
                if hasattr(self.__spi, "deinit"):
                    self.__spi.deinit()
            except Exception:
                pass
        else:
            try:
                self.__spi.close()
            except Exception:
                pass
        self.__spi = None

    def write(self, reg, data):
        try:
            reg &= 0x7F # clear RW bit
            writeData = reg.to_bytes(1, "little") + data
            if self.__micropython:
                try:
                    self.__cs(0)
                    self.__spi.write(writeData)
                finally:
                    self.__cs(1)
            else:
                self.__spi.xfer2(writeData)
        except Exception as e:
            raise BME280Error("BME280: SPI error: %s" % str(e))

    def read(self, reg, length):
        try:
            reg |= 0x80 # set RW bit
            if self.__micropython:
                try:
                    self.__cs(0)
                    return memoryview(self.__spi.read(length + 1, reg))[1:]
                finally:
                    self.__cs(1)
            else:
                writeData = reg.to_bytes(1, "little") * (length + 1)
                return memoryview(self.__spi.xfer2(writeData))[1:]
        except Exception as e:
            raise BME280Error("BME280: SPI error: %s" % str(e))

# Registers
_REG_dig_T1         = const(0x88) # 16 bit LE
_REG_dig_T2         = const(0x8A) # 16 bit LE
_REG_dig_T3         = const(0x8C) # 16 bit LE
_REG_dig_P1         = const(0x8E) # 16 bit LE
_REG_dig_P2         = const(0x90) # 16 bit LE
_REG_dig_P3         = const(0x92) # 16 bit LE
_REG_dig_P4         = const(0x94) # 16 bit LE
_REG_dig_P5         = const(0x96) # 16 bit LE
_REG_dig_P6         = const(0x98) # 16 bit LE
_REG_dig_P7         = const(0x9A) # 16 bit LE
_REG_dig_P8         = const(0x9C) # 16 bit LE
_REG_dig_P9         = const(0x9E) # 16 bit LE
_REG_dig_H1         = const(0xA1) # 8 bit
_REG_id             = const(0xD0) # 8 bit
_REG_reset          = const(0xE0) # 8 bit
_REG_dig_H2         = const(0xE1) # 16 bit LE
_REG_dig_H3         = const(0xE3) # 8 bit
_REG_dig_H4         = const(0xE4) # 12 bit BE (overlaps with next)
_REG_dig_H5         = const(0xE5) # 12 bit LE (overlaps with previous)
_REG_dig_H6         = const(0xE7) # 8 bit
_REG_ctrl_hum       = const(0xF2) # 8 bit
_REG_status         = const(0xF3) # 8 bit
_REG_ctrl_meas      = const(0xF4) # 8 bit
_REG_config         = const(0xF5) # 8 bit
_REG_press_msb      = const(0xF7) # 8 bit
_REG_press_lsb      = const(0xF8) # 8 bit
_REG_press_xlsb     = const(0xF9) # 8 bit
_REG_temp_msb       = const(0xFA) # 8 bit
_REG_temp_lsb       = const(0xFB) # 8 bit
_REG_temp_xlsb      = const(0xFC) # 8 bit
_REG_hum_msb        = const(0xFD) # 8 bit
_REG_hum_lsb        = const(0xFE) # 8 bit

# Operation mode
MODE_SLEEP          = const(0b00)
MODE_FORCED         = const(0b01)
MODE_NORMAL         = const(0b11)

# Oversampling (osrs_h, osrs_p, osrs_t)
OVSMPL_SKIP         = const(0b000) # measurement turned off
OVSMPL_1            = const(0b001)
OVSMPL_2            = const(0b010)
OVSMPL_4            = const(0b011)
OVSMPL_8            = const(0b100)
OVSMPL_16           = const(0b101)

# Standby time (t_sb)
T_SB_p5ms           = const(0b000) # 0.5 ms
T_SB_10ms           = const(0b110) # 10 ms
T_SB_20ms           = const(0b111) # 20 ms
T_SB_62p5ms         = const(0b001) # 62.5 ms
T_SB_125ms          = const(0b010) # 125 ms
T_SB_250ms          = const(0b011) # 250 ms
T_SB_500ms          = const(0b100) # 500 ms
T_SB_1000ms         = const(0b101) # 1 s

# Filter settings
FILTER_OFF          = const(0b000)
FILTER_2            = const(0b001)
FILTER_4            = const(0b010)
FILTER_8            = const(0b011)
FILTER_16           = const(0b100)

# Calculation mode for compensation functions.
CALC_FLOAT          = const(0)
CALC_INT32          = const(1)
CALC_INT64          = const(2)

class BME280:
    """BME280 device driver.
    """
    __slots__ = (
        "__calc",
        "__bus",
        "__resetPending",
        "__cal_dig_T1",
        "__cal_dig_T2",
        "__cal_dig_T3",
        "__cal_dig_P1",
        "__cal_dig_P2",
        "__cal_dig_P3",
        "__cal_dig_P4",
        "__cal_dig_P5",
        "__cal_dig_P6",
        "__cal_dig_P7",
        "__cal_dig_P8",
        "__cal_dig_P9",
        "__cal_dig_H1",
        "__cal_dig_H2",
        "__cal_dig_H3",
        "__cal_dig_H4",
        "__cal_dig_H5",
        "__cal_dig_H6",
        "__cache_config",
        "__cache_ctrl_hum",
    )

    def __init__(self,
                 i2cBus=None,
                 i2cAddr=0x76,
                 spiBus=None,
                 spiCS=None,
                 busFreq=100,
                 calc=(CALC_INT32 if isMicropython else CALC_FLOAT)):
        """Create BME280 driver instance.
        'i2cBus': I2C hardware bus index to use for communication with the device.
                  Or dict { "scl": 1, "sda": 2 } of pin numbers for software I2C.
                  Or dict { "index": 0, "scl": 1, "sda": 2 } for hardware I2C-0 with different pinning.
                  Or a fully initialized Micropython I2C/SoftI2C object.
                  Pin numbers may either be integers or Micropython Pin objects.
        'i2cAddr': I2C address of the device. May be 0x76 or 0x77.
        'spiBus': SPI hardware bus index to use for communication with the device.
                  Or dict { "sck": 1, "mosi": 2, "miso": 3 } of pin numbers for software SPI.
                  Or dict { "index": 0, "sck": 1, "mosi": 2, "miso": 3 } for hardware SPI-0 with different pinning.
                  Or a fully initialized Micropython SPI/SoftSPI object.
                  Pin numbers may either be integers or Micropython Pin objects.
        'spiCS': SPI chip select identifier number or pin number or Micropython Pin object.
        'busFreq': I2C/SPI bus clock frequency, in kHz.
        'calc': Calculation mode for compensation functions. One of CALC_...
        """
        self.__calc = calc
        if i2cBus is not None:
            self.__bus = BME280I2C(i2cBus, i2cAddr, busFreq)
        elif spiBus is not None:
            self.__bus = BME280SPI(spiBus, spiCS, busFreq)
        else:
            raise BME280Error("BME280: No bus configured.")
        self.__resetPending = True

    async def closeAsync(self):
        """Shutdown communication to the device.
        """
        if self.__bus:
            try:
                await self.startAsync(mode=MODE_SLEEP)
            except BME280Error:
                pass
            self.__bus.close()
            self.__bus = None
        self.__resetPending = True

    def close(self):
        """Shutdown communication to the device.
        """
        asyncio.run(self.closeAsync())

    def __enter__(self):
        return self

    async def __aenter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.closeAsync()

    def __readCal(self):
        """Read the calibration data from the device.
        """
        data = bytes(self.__readBurst(_REG_dig_T1, _REG_dig_H1))
        data += bytes(self.__readBurst(_REG_dig_H2, _REG_dig_H6))

        def twos(value, bits):
            """Convert a raw value represented in two's complement to signed Python int.
            'bits': The length of the raw value.
            """
            mask = (1 << bits) - 1
            value &= mask
            if value & (1 << (bits - 1)):
                return -((~value + 1) & mask)
            return value

        def getU8(reg):
            if reg >= _REG_dig_H2:
                return data[(reg - _REG_dig_H2) + (_REG_dig_H1 - _REG_dig_T1 + 1)]
            return data[reg - _REG_dig_T1]

        def getS8(reg):
            return twos(getU8(reg), 8)

        def getU16LE(reg):
            return (getU8(reg + 1) << 8) | getU8(reg)

        def getS16LE(reg):
            return twos(getU16LE(reg), 16)

        def getS12BE(reg):
            return twos((getU8(reg) << 4) | (getU8(reg + 1) & 0xF), 12)

        def getS12LE(reg):
            return twos((getU8(reg + 1) << 4) | (getU8(reg) >> 4), 12)

        def cal(x):
            return float(x) if self.__calc == CALC_FLOAT else x

        self.__cal_dig_T1 = cal(getU16LE(_REG_dig_T1))
        self.__cal_dig_T2 = cal(getS16LE(_REG_dig_T2))
        self.__cal_dig_T3 = cal(getS16LE(_REG_dig_T3))
        self.__cal_dig_P1 = cal(getU16LE(_REG_dig_P1))
        self.__cal_dig_P2 = cal(getS16LE(_REG_dig_P2))
        self.__cal_dig_P3 = cal(getS16LE(_REG_dig_P3))
        self.__cal_dig_P4 = cal(getS16LE(_REG_dig_P4))
        self.__cal_dig_P5 = cal(getS16LE(_REG_dig_P5))
        self.__cal_dig_P6 = cal(getS16LE(_REG_dig_P6))
        self.__cal_dig_P7 = cal(getS16LE(_REG_dig_P7))
        self.__cal_dig_P8 = cal(getS16LE(_REG_dig_P8))
        self.__cal_dig_P9 = cal(getS16LE(_REG_dig_P9))
        self.__cal_dig_H1 = cal(getU8(_REG_dig_H1))
        self.__cal_dig_H2 = cal(getS16LE(_REG_dig_H2))
        self.__cal_dig_H3 = cal(getU8(_REG_dig_H3))
        self.__cal_dig_H4 = cal(getS12BE(_REG_dig_H4))
        self.__cal_dig_H5 = cal(getS12LE(_REG_dig_H5))
        self.__cal_dig_H6 = cal(getS8(_REG_dig_H6))

    async def resetAsync(self):
        """Reset the device.
        This is a coroutine.
        """
        if not self.__bus:
            raise BME280Error("BME280: Device not opened.")
        self.__cache_config = None
        self.__cache_ctrl_hum = None

        self.__write8(_REG_reset, 0xB6)
        await asyncio.sleep(0.05)
        for _ in range(5):
            if self.__readU8(_REG_id) == 0x60:
                break
            await asyncio.sleep(0.01)
        else:
            raise BME280Error("BME280: ID register response incorrect.")
        for _ in range(5):
            im_update, measuring = self.__read_status()
            if not im_update and not measuring:
                break
            await asyncio.sleep(0.01)
        else:
            raise BME280Error("BME280: status register response incorrect.")
        self.__readCal()
        self.__resetPending = False

    def reset(self):
        """Synchronously call the coroutine resetAsync().
        See resetAsync() for documentation about behaviour, arguments and return value.
        """
        asyncio.run(self.resetAsync())

    async def startAsync(self,
                         mode,
                         standbyTime=T_SB_125ms,
                         filter=FILTER_OFF,
                         tempOversampling=OVSMPL_1,
                         humidityOversampling=OVSMPL_1,
                         pressureOversampling=OVSMPL_1):
        """Reconfigure the device.
        'mode': Operation mode. MODE_SLEEP, MODE_FORCED or MODE_NORMAL.
        'standbyTime': Standby time. One of T_SB_...
        'filter': Filter configuration. One of FILTER_...
        'tempOversampling': Temperature oversampling. One of OVSMPL_...
        'humidityOversampling': Humidity oversampling. One of OVSMPL_...
        'pressureOversampling': Pressure oversampling. One of OVSMPL_...
        By default this starts in MODE_SLEEP.
        """
        if not self.__bus:
            raise BME280Error("BME280: Device not opened.")
        if self.__resetPending:
            await self.resetAsync()
        self.__write_config(t_sb=standbyTime,
                            filter=filter,
                            spi3w_en=False)
        self.__write_ctrl_hum(osrs_h=humidityOversampling)
        self.__write_ctrl_meas(osrs_t=tempOversampling,
                               osrs_p=pressureOversampling,
                               mode=mode)

    def start(self, *args, **kwargs):
        """Synchronously call the coroutine startAsync().
        See startAsync() for documentation about behaviour, arguments and return value.
        """
        asyncio.run(self.startAsync(*args, **kwargs))

    async def readForcedAsync(self, *, pollSleep=0.05, **kwargs):
        """Trigger a MODE_FORCED conversion,
        wait for it to complete and return the same as read().
        This is a coroutine.
        """
        if not self.__bus:
            raise BME280Error("BME280: Device not opened.")
        await self.startAsync(**kwargs, mode=MODE_FORCED)
        while await self.isMeasuringAsync():
            await asyncio.sleep(pollSleep)
        return await self.readAsync()

    def readForced(self, *args, **kwargs):
        """Synchronously call the coroutine readForcedAsync().
        See readForcedAsync() for documentation about behaviour, arguments and return value.
        """
        return asyncio.run(self.readForcedAsync(*args, **kwargs))

    async def isMeasuringAsync(self):
        """Returns True, if the device is currently running the measurement cycle.
        In MODE_FORCED: If this returns False, it's Ok to read() the new data.
        """
        if not self.__bus:
            raise BME280Error("BME280: Device not opened.")
        im_update, measuring = self.__read_status()
        return measuring

    def isMeasuring(self):
        """Synchronously call the coroutine isMeasuringAsync().
        See isMeasuringAsync() for documentation about behaviour, arguments and return value.
        """
        return asyncio.run(self.isMeasuringAsync())

    async def readAsync(self):
        """Read the temperature, humidity and pressure from the device.
        Returns a tuple (temperature, humidity, pressure).
        temparature in degree Celsius.
        humitidy as value between 0 and 1. 0.0 = 0% -> 1.0 = 100%.
        pressure in Pascal.
        """
        if not self.__bus:
            raise BME280Error("BME280: Device not opened.")

        # Read the raw registers.
        data = self.__readBurst(_REG_press_msb, _REG_hum_lsb)
        def get(reg):
            return data[reg - _REG_press_msb]

        # Extract raw pressure.
        up = ((get(_REG_press_msb) << 12) |
              (get(_REG_press_lsb) << 4) |
              (get(_REG_press_xlsb) >> 4))

        # Extract raw temperature.
        ut = ((get(_REG_temp_msb) << 12) |
              (get(_REG_temp_lsb) << 4) |
              (get(_REG_temp_xlsb) >> 4))

        # Extract raw humidity.
        uh = ((get(_REG_hum_msb) << 8) |
              get(_REG_hum_lsb))

        # Run compensations.
        t_fine, t = self.__compT(ut)
        h = self.__compH(t_fine, uh)
        p = self.__compP(t_fine, up)

        return t, h, p

    def read(self):
        """Synchronously call the coroutine readAsync().
        See readAsync() for documentation about behaviour, arguments and return value.
        """
        return asyncio.run(self.readAsync())

    def __compT(self, ut):
        """Convert the uncompensated temperature 'ut'
        to compensated degree Celsius.
        """
        if self.__calc == CALC_FLOAT:
            t_fine, t = self.__compT_float(ut)
        else:
            t_fine, t = self.__compT_int32(ut)
            t = float(t) * 1e-2
        return t_fine, min(max(t, -40.0), 85.0)

    def __compT_float(self, ut):
        ut = float(ut)
        T1 = self.__cal_dig_T1
        T2 = self.__cal_dig_T2
        T3 = self.__cal_dig_T3
        a = (ut / 16384.0 - T1 / 1024.0) * T2
        b = ut / 131072.0 - T1 / 8192.0
        b *= b * T3
        t_fine = a + b
        t = t_fine / 5120.0
        return int(t_fine), t

    @micropython.viper
    def __compT_int32(self, ut: int):
        T1 = int(self.__cal_dig_T1)
        T2 = int(self.__cal_dig_T2)
        T3 = int(self.__cal_dig_T3)
        a = (((ut >> 3) - (T1 << 1)) * T2) >> 11
        b = (ut >> 4) - T1
        b = (((b * b) >> 12) * T3) >> 14
        t_fine = a + b
        t = (t_fine * 5 + 128) >> 8
        return t_fine, t

    def __compP(self, t_fine, up):
        """Convert the uncompensated pressure 'up' to compensated Pascal.
        't_fine' is the high resolution temperature.
        """
        if self.__calc == CALC_FLOAT:
            p = self.__compP_float(t_fine, up)
        elif self.__calc == CALC_INT32:
            p = float(self.__compP_int32(t_fine, up))
        else:
            p = self.__compP_int64(t_fine, up) / 256.0
        return min(max(p, 30000.0), 110000.0)

    def __compP_float(self, t_fine, up):
        up = float(up)
        P1 = self.__cal_dig_P1
        P2 = self.__cal_dig_P2
        P3 = self.__cal_dig_P3
        P4 = self.__cal_dig_P4
        P5 = self.__cal_dig_P5
        P6 = self.__cal_dig_P6
        P7 = self.__cal_dig_P7
        P8 = self.__cal_dig_P8
        P9 = self.__cal_dig_P9
        a = (t_fine / 2.0) - 64000.0
        b = a * a * P6 / 32768.0
        b += a * P5 * 2.0
        b = (b / 4.0) + (P4 * 65536.0)
        a = (P3 * a * a / 524288.0 + P2 * a) / 524288.0
        a = (1.0 + a / 32768.0) * P1
        if a:
            p = ((1048576.0 - up) - (b / 4096.0)) * 6250.0 / a
            a = P9 * p * p / 2147483648.0
            b = p * P8 / 32768.0
            p = p + (a + b + P7) / 16.0
            return p
        return 0.0

    @micropython.viper
    def __compP_int32(self, t_fine: int, up: int) -> int:
        P1 = int(self.__cal_dig_P1)
        P2 = int(self.__cal_dig_P2)
        P3 = int(self.__cal_dig_P3)
        P4 = int(self.__cal_dig_P4)
        P5 = int(self.__cal_dig_P5)
        P6 = int(self.__cal_dig_P6)
        P7 = int(self.__cal_dig_P7)
        P8 = int(self.__cal_dig_P8)
        P9 = int(self.__cal_dig_P9)
        a = (t_fine >> 1) - 64000
        c = a >> 2
        b = ((c * c) >> 11) * P6
        b += (a * P5) << 1
        b = (b >> 2) + (P4 << 16)
        a = (((P3 * ((c * c) >> 13)) >> 3) + ((P2 * a) >> 1)) >> 18
        a = ((32768 + a) * P1) >> 15
        if a:
            p = ((((1048576 - up) - (b >> 12)) * 3125) // a) << 1
            c = p >> 3
            a = (P9 * ((c * c) >> 13)) >> 12
            b = (P8 * (p >> 2)) >> 13
            p += (a + b + P7) >> 4
            return p
        return 0

    @micropython.native
    def __compP_int64(self, t_fine, up):
        P1 = self.__cal_dig_P1
        P2 = self.__cal_dig_P2
        P3 = self.__cal_dig_P3
        P4 = self.__cal_dig_P4
        P5 = self.__cal_dig_P5
        P6 = self.__cal_dig_P6
        P7 = self.__cal_dig_P7
        P8 = self.__cal_dig_P8
        P9 = self.__cal_dig_P9
        a = t_fine - 128000
        b = a * a * P6
        b = b + ((a * P5) << 17)
        b = b + (P4 << 35)
        a = ((a * a * P3) >> 8) + ((a * P2) << 12)
        a = (((1 << 47) + a) * P1) >> 33
        if a:
            p = ((((1048576 - up) << 31) - b) * 3125) // a
            c = p >> 13
            a = (P9 * c * c) >> 25
            b = (P8 * p) >> 19
            p = ((p + a + b) >> 8) + (P7 << 4)
            return p
        return 0

    def __compH(self, t_fine, uh):
        """Convert the uncompensated relative humidity 'uh'
        to compensated relative humidity 0.0 = 0% -> 1.0 = 100%.
        't_fine' is the high resolution temperature.
        """
        if self.__calc == CALC_FLOAT:
            h = self.__compH_float(t_fine, uh) * 1e-2
        else:
            h = self.__compH_int32(t_fine, uh) / 102400.0
        return min(max(h, 0.0), 1.0)

    def __compH_float(self, t_fine, uh):
        uh = float(uh)
        H1 = self.__cal_dig_H1
        H2 = self.__cal_dig_H2
        H3 = self.__cal_dig_H3
        H4 = self.__cal_dig_H4
        H5 = self.__cal_dig_H5
        H6 = self.__cal_dig_H6
        a = uh - (H4 * 64.0 + H5 / 16384.0 * (t_fine - 76800.0))
        a *= H2 / 65536.0 * (1.0 + H6 / 67108864.0 * a * (1.0 + H3 / 67108864.0 * a))
        a *= 1.0 - H1 * a / 524288.0
        return a

    @micropython.viper
    def __compH_int32(self, t_fine: int, uh: int) -> int:
        H1 = int(self.__cal_dig_H1)
        H2 = int(self.__cal_dig_H2)
        H3 = int(self.__cal_dig_H3)
        H4 = int(self.__cal_dig_H4)
        H5 = int(self.__cal_dig_H5)
        H6 = int(self.__cal_dig_H6)
        a = (((uh << 14) - (H4 << 20) - (H5 * (t_fine - 76800))) + 0x4000) >> 15
        a *= ((((((a * H6) >> 10) * (((a * H3) >> 11) + 0x8000)) >> 10) + 0x200000) * H2 + 0x2000) >> 14
        a -= ((((a >> 15) * (a >> 15)) >> 7) * H1) >> 4
        return a >> 12

    def __read_status(self):
        """Read 'status' register.
        """
        status = self.__readU8(_REG_status)
        im_update = bool(status & (1 << 0))
        measuring = bool(status & (1 << 3))
        return im_update, measuring

    def __write_config(self, t_sb, filter, spi3w_en):
        """Write the 'config' register.
        """
        data = ((t_sb & 7) << 5) | ((filter & 7) << 2) | (spi3w_en & 1)
        if data != self.__cache_config:
            self.__write8(_REG_config, data)
            self.__cache_config = data

    def __write_ctrl_meas(self, osrs_t, osrs_p, mode):
        """Write the 'ctrl_meas' register.
        """
        data = ((osrs_t & 7) << 5) | ((osrs_p & 7) <<  2) | (mode & 3)
        self.__write8(_REG_ctrl_meas, data)

    def __write_ctrl_hum(self, osrs_h):
        """Write the 'ctrl_hum' register.
        """
        data = osrs_h & 7
        if data != self.__cache_ctrl_hum:
            self.__write8(_REG_ctrl_hum, data)
            self.__cache_ctrl_hum = data

    def __readU8(self, reg):
        """Read a register and interpret the value as unsigned 8-bit.
        """
        return self.__bus.read(reg, 1)[0]

    def __readBurst(self, startReg, endReg):
        """Read multiple registers with a burst transfer.
        """
        assert endReg >= startReg
        length = (endReg - startReg) + 1
        return self.__bus.read(startReg, length)

    def __write8(self, reg, value):
        """Write an 8-bit register.
        """
        self.__bus.write(reg, (value & 0xFF).to_bytes(1, "little"))

# vim: ts=4 sw=4 expandtab
