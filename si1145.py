#!/usr/bin/python3

# from ops_i2cbase import I2CBase

from Adafruit_I2C import Adafruit_I2C


# ===========================================================================
# SI1145 Class
#
# Ported from github.com/adafruit/Adafruit_SI1145_Library/
# ===========================================================================

class SI1145:
    i2c = None

    # SI1145 Address
    # address = 0x60

    # Commands
    SI1145_PARAM_QUERY = 0x80
    SI1145_PARAM_SET = 0xA0

    SI1145_PSALS_AUTO = 0x0F

    # Parameters
    SI1145_PARAM_I2CADDR = 0x00
    SI1145_PARAM_CHLIST = 0x01
    SI1145_PARAM_CHLIST_ENUV = 0x80
    SI1145_PARAM_CHLIST_ENAUX = 0x40
    SI1145_PARAM_CHLIST_ENALSIR = 0x20
    SI1145_PARAM_CHLIST_ENALSVIS = 0x10
    SI1145_PARAM_CHLIST_ENPS1 = 0x01
    SI1145_PARAM_CHLIST_ENPS2 = 0x02
    SI1145_PARAM_CHLIST_ENPS3 = 0x04

    # Registers
    SI1145_REG_PARTID = 0x00
    SI1145_REG_SEQID = 0x02

    SI1145_REG_UCOEFF0 = 0x13
    SI1145_REG_UCOEFF1 = 0x14
    SI1145_REG_UCOEFF2 = 0x15
    SI1145_REG_UCOEFF3 = 0x16
    SI1145_REG_PARAMWR = 0x17
    SI1145_REG_COMMAND = 0x18

    SI1145_REG_MEASRATE0 = 0x08
    SI1145_REG_MEASRATE1 = 0x09

    # Constructor
    def __init__(self, address=0x60, mode=1, bus=1, debug=False):
        # I2C
        self.i2c = Adafruit_I2C(address, bus)
        self.debug = debug

        part_id = self.i2c.readU8(self.SI1145_REG_PARTID)
        if part_id != 0x45:
            print("SI1145 is not found")

        if self.debug:
            seq_id = self.i2c.readU8(self.SI1145_REG_SEQID)
            print("DBG : SI1145 SEQ ID = %x" % seq_id)


        # to enable UV reading, set the EN_UV bit in CHLIST,
        # and configure UCOEF [0:3] to the default values of 0x7B, 0x6B, 0x01, and 0x00

        self.i2c.write8(self.SI1145_REG_UCOEFF0, 0x7B)
        self.i2c.write8(self.SI1145_REG_UCOEFF1, 0x6B)
        self.i2c.write8(self.SI1145_REG_UCOEFF2, 0x01)
        self.i2c.write8(self.SI1145_REG_UCOEFF3, 0x00)
        """
        self.i2c.write8(self.SI1145_REG_UCOEFF0, 0x00)
        self.i2c.write8(self.SI1145_REG_UCOEFF1, 0x02)
        self.i2c.write8(self.SI1145_REG_UCOEFF2, 0x89)
        self.i2c.write8(self.SI1145_REG_UCOEFF3, 0x29)
        """
        # enable UV sensor
        self.i2c.write8(self.SI1145_REG_PARAMWR,
                        self.SI1145_PARAM_CHLIST_ENUV | self.SI1145_PARAM_CHLIST_ENALSIR |
                        self.SI1145_PARAM_CHLIST_ENALSVIS | self.SI1145_PARAM_CHLIST_ENPS1)
        self.i2c.write8(self.SI1145_REG_COMMAND, self.SI1145_PARAM_CHLIST | self.SI1145_PARAM_SET)

        # measurement rate for auto
        self.i2c.write8(self.SI1145_REG_MEASRATE0, 0xFF)

        # auto run
        self.i2c.write8(self.SI1145_REG_COMMAND, self.SI1145_PSALS_AUTO)

    def readUVIndex(self):
        """Read UV index data from sensor (UV index * 100)"""


        if self.debug:
            rawdataUV0 = self.i2c.readU8(0x2C)
            rawdataUV1 = self.i2c.readU8(0x2D)
            print("DBG : UV_lowByte  is %x" % rawdataUV0)
            print("DBG : UV_highByte is %x" % rawdataUV1)

        # The original code gave wrong readings. According to datasheet, the low byte comes first (@ 0x2C)
        # and afterwards the high byte. So it needs to be reversed.
        rawData = self.i2c.reverseByteOrder(self.i2c.readU16(0x2C))

#         uv_index = int(rawData)

        if self.debug:
            print("DBG : UV index is %s" % rawData)

        return rawData

    def readAmbientLight(self):
        """Read Ambient Light data from sensor (Visible light + IR) in lux"""

        # The original code gave wrong readings. According to datasheet, the low byte comes first (@ 0x2C)
        # and afterwards the high byte. So it needs to be reversed.
        rawData = self.i2c.reverseByteOrder(self.i2c.readU16(0x22))

        if self.debug:
            print("Ambient Light is %d lux" % rawData)

        return rawData

    def readIRLight(self):
        """Read IR data from sensor in lux"""

        # The original code gave wrong readings. According to datasheet, the low byte comes first (@ 0x2C)
        # and afterwards the high byte. So it needs to be reversed.
        rawData = self.i2c.reverseByteOrder(self.i2c.readU16(0x24))
        if self.debug:
            print("IR Light is %d lux" % rawData)

        return rawData
