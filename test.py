#!/usr/bin/env python3
"""TODO."""

import UBX
from UBXMessage import parseUBXMessage

if __name__ == '__main__':

    print("UBX.CFG.PMS.Get: ", UBX.CFG.PMS.Get().serialize())

    print("UBX.CFG.PMS.Set: ", UBX.CFG.PMS.Set(powerSetupValue=2).serialize())

    print("UBX.MON.VER.Get: ", UBX.MON.VER.Get().serialize())

    print("UBX.TEST.TEST.Get: ", UBX.TEST.TEST.Get().serialize())

    print(parseUBXMessage(0x05, 0x01, b'12'))

    print(parseUBXMessage(0x05, 0x00, b'gh'))

    print(parseUBXMessage(0xff, 0xff, b'gh0011'))
