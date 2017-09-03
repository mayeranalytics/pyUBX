#!/usr/bin/env python3
"""TODO."""

import UBX
from UBXMessage import parseUBXMessage

if __name__ == '__main__':

    setPMS = UBX.CFG.PMS.Set(powerSetupValue=2).serialize()
    print(setPMS)

    getVER = UBX.MON.VER.Req().serialize()
    print(getVER)

    print(parseUBXMessage(0x05, 0x01, b'12'))
