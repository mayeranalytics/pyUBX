#!/usr/bin/env python3
"""TODO."""

import sys
import os
import serial
from time import sleep
from UBXManager import UBXManager
import UBX
import argparse


class Manager(UBXManager):
    def __init__(self, debug=debug):
        UBXManager.__init__(debug)
    def onUBX(self, obj):
        print(obj)
    def onUBXError(self, msgClass, msgId, errMsg):
        print(msgClass, msgId, errMsg)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Send UBX commands to u-blox M8 device.'
        )
    parser.add_argument(
        '--VER', dest='VER', action='store_true',
        help='Get the version string'
        )
    parser.add_argument(
        '--RXM', dest='RXM', action='store',
        help='Set the power mode (0=cont, 1=save)'
        )
    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true',
        help='Turn on debug mode'
        )
    args = parser.parse_args()

    todo = []
    if args.VER: todo.append(("VER", None))
    if args.RXM is not None: todo.append(("RXM", args.RXM))

    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=None)
    debug = (os.environ.get("DEBUG") is not None) or args.debug

    manager = Manager(ser, debug=debug)
    manager.start()
    sys.stderr.write("started UBXManager\n")

    getVER = UBX.MON.VER.Get().serialize()
    setPMS = UBX.CFG.PMS.Set(powerSetupValue=2).serialize()
    getPMS = UBX.CFG.PMS.Get().serialize()
    getGNSS = UBX.CFG.GNSS.Get().serialize()
    getRMX = UBX.CFG.RMX.Get().serialize()

    sleep(2)
    sys.stderr.write("sending UBX.MON.VER.Get\n")
    manager.send(getVER)

    sleep(2)
    sys.stderr.write("sending UBX.CFG.GNSS.Get\n")
    manager.send(getGNSS)

    sleep(2)
    sys.stderr.write("sending UBX.CFG.PMS.Get\n")
    manager.send(getPMS)

    sleep(2)
    sys.stderr.write("sending UBX.CFG.RMX.Get\n")
    manager.send(getRMX)

    manager.join()
