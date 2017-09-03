#!/usr/bin/env python3
"""TODO."""

import sys
import os
import serial
from time import sleep
from UBXManager import UBXManager
from UBXMessage import UBX

if __name__ == '__main__':

    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=None)
    debug = os.environ.get("DEBUG") is not None

    manager = UBXManager(ser)
    manager.start()
    sys.stderr.write("started UBXManager\n")

    setPMS = UBX.CFG.PMS.Set(powerSetupValue=2).serialize()
    reqPMS = UBX.CFG.PMS.Req().serialize()
    reqGNSS = UBX.CFG.GNSS.Req().serialize()

    sleep(1)
    sys.stderr.write("sending UBX.CFG.GNSS.Req\n")
    manager.send(reqGNSS)

    sleep(1)
    sys.stderr.write("sending UBX.CFG.PMS.Set\n")
    manager.send(reqPMS)

    manager.join()
