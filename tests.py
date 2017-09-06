#!/usr/bin/env python3
"""Unit tests."""

import unittest
import UBX
from UBXMessage import parseUBXPayload, parseUBXMessage


class TestStringMethods(unittest.TestCase):

    def testClassId1(self):
        getVer = UBX.MON.VER.Get()
        self.assertEqual(getVer._class, 0x0A)
        self.assertEqual(getVer._id, 0x04)

    def testClassId2(self):
        self.assertEqual(UBX.MON._class, 0x0A)
        self.assertEqual(UBX.MON.VER._class, 0x0A)
        self.assertEqual(UBX.MON.VER._id, 0x04)

    def testRXM(self):
        rxm = UBX.CFG.RXM(b'\x48\x00')
        self.assertEqual(rxm.reserved1, 0x48)
        self.assertEqual(rxm.lpMode, 0x00)
        rxm.lpMode = 1
        msg = rxm.serialize()
        rxm2 = parseUBXMessage(msg)
        self.assertEqual(rxm.reserved1, 0x48)
        self.assertEqual(rxm.lpMode, 0x01)

    def testMON_VER(self):
        payload = b'\x52\x4f\x4d\x20\x43\x4f\x52\x45\x20\x33\x2e\x30\x31\x20\x28\x31\x30\x37\x38\x38\x38\x29\x00\x00\x00\x00\x00\x00\x00\x00\x30\x30\x30\x38\x30\x30\x30\x30\x00\x00\x46\x57\x56\x45\x52\x3d\x53\x50\x47\x20\x33\x2e\x30\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x50\x52\x4f\x54\x56\x45\x52\x3d\x31\x38\x2e\x30\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x47\x50\x53\x3b\x47\x4c\x4f\x3b\x47\x41\x4c\x3b\x42\x44\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x53\x42\x41\x53\x3b\x49\x4d\x45\x53\x3b\x51\x5a\x53\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        ver = parseUBXPayload(UBX.MON._class, UBX.MON.VER._id, payload)
        self.assertEqual(ver.swVersion, "ROM CORE 3.01 (107888)")
        self.assertEqual(ver.hwVersion, "00080000")
        self.assertEqual(ver.extension_1, "FWVER=SPG 3.01")
        self.assertEqual(ver.extension_2, "PROTVER=18.00")
        self.assertEqual(ver.extension_3, "GPS;GLO;GAL;BDS")
        self.assertEqual(ver.extension_4, "SBAS;IMES;QZSS")

    def testCFG_GNSS(self):
        payload = b'\x00\x20\x20\x07\x00\x08\x10\x00\x01\x00\x01\x01\x01\x01\x03\x00\x01\x00\x01\x01\x02\x04\x08\x00\x00\x00\x01\x01\x03\x08\x10\x00\x00\x00\x01\x01\x04\x00\x08\x00\x00\x00\x01\x03\x05\x00\x03\x00\x01\x00\x01\x05\x06\x08\x0e\x00\x01\x00\x01\x01'
        gnss = parseUBXPayload(UBX.CFG._class, UBX.CFG.GNSS._id, payload)
        self.assertEqual(gnss.msgVer, 0x00)
        self.assertEqual(gnss.numConfigBlocks, 0x07)
        self.assertEqual(gnss.maxTrkCh_1, 0x10)
        self.assertEqual(gnss.flags_4, 0x01010000)
        self.assertEqual(gnss.maxTrkCh_7, 0x0E)


if __name__ == '__main__':
    unittest.main()
