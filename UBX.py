#!/usr/bin/env python3
"""TODO."""

import sys
import os
import serial
from time import sleep
from UBXManager import UBXManager
import UBX

if __name__ == '__main__':

    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=None)
    debug = os.environ.get("DEBUG") is not None

    manager = UBXManager(ser, debug=debug)
    manager.start()
    sys.stderr.write("started UBXManager\n")

    getVER = UBX.MON.VER.Get().serialize()
    setPMS = UBX.CFG.PMS.Set(powerSetupValue=2).serialize()
    getPMS = UBX.CFG.PMS.Get().serialize()
    getGNSS = UBX.CFG.GNSS.Get().serialize()

    sleep(2)
    sys.stderr.write("sending UBX.MON.VER.Get\n")
    manager.send(getVER)

    sleep(2)
    sys.stderr.write("sending UBX.CFG.GNSS.Get\n")
    manager.send(getGNSS)

    sleep(2)
    sys.stderr.write("sending UBX.CFG.PMS.Get\n")
    manager.send(getPMS)

    manager.join()
