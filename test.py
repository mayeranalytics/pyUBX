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

    print(parseUBXMessage(UBX.TEST._class, UBX.TEST.TEST._id,
                          b'\x80\xff\x01\x00\x02\x00'))

    msg = b'\x00\x20\x20\x07\x00\x08\x10\x00\x01\x00\x01\x01\x01\x01\x03\x00\x01\x00\x01\x01\x02\x04\x08\x00\x00\x00\x01\x01\x03\x08\x10\x00\x00\x00\x01\x01\x04\x00\x08\x00\x00\x00\x01\x03\x05\x00\x03\x00\x01\x00\x01\x05\x06\x08\x0e\x00\x01\x00\x01\x01'
    print(parseUBXMessage(UBX.CFG._class, UBX.CFG.GNSS._id, msg))    # CFG-GNSS
