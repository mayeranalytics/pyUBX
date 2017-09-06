#!/usr/bin/env python3
"""TODO."""

import sys
import os
import serial
from time import sleep
from threading import Lock
from enum import Enum
import argparse
import UBX
from UBXManager import UBXManager


class FSM_VER_Get:
    """FSM handling MON.VER.Get"""
    _class = UBX.MON.VER._class
    _id = UBX.MON.VER._id
    class STATE(Enum):
        START = 0
        DONE = 1
    def __init__(self):
        self.state = FSM_VER_Get.STATE.START
        self.ver = None
    def done(self):
        return self.state == FSM_VER_Get.STATE.DONE
    def onUBX(self, obj, manager):
        if obj._class == FSM_VER_Get._class and obj._id == FSM_VER_Get._id:
            print(obj)
            self.state = FSM_VER_Get.STATE.DONE


def isObj(obj, cls):
    return obj._class == cls._class and obj._id == cls._id


def isACK(obj):
    """Test whether message obj is a ACK."""
    return isObj(obj, UBX.ACK.ACK)


def isNAK(obj):
    """Test whether message obj is a NAK."""
    return isObj(obj, UBX.ACK.NAK)


class FSM_RXM_Set:
    """FSM handling MON.VER.Get"""
    _class = UBX.CFG.RXM._class
    _id = UBX.CFG.RXM._id
    class STATE(Enum):
        START = 0
        WAIT_GET = 1
        WAIT_GET_ACK = 2
        WAIT_SET_ACK = 3
        DONE = 4
    def __init__(self, lpMode):
        self.state = FSM_RXM_Set.STATE.START
        self.ver = None
        self._gottenObj = None
        self.lpMode = lpMode
    def done(self):
        return self.state == FSM_RXM_Set.STATE.DONE
    def onUBX(self, obj, manager):
        if self.state == FSM_RXM_Set.STATE.START:
            print("START->\n", obj)
            if isObj(obj, UBX.CFG.RXM):
                self._gottenObj = obj
                self.state = FSM_RXM_Set.STATE.WAIT_GET_ACK
            else:
                print("Didnt' get a UBX.CFG.RXM")
                self.state = FSM_RXM_Set.STATE.DONE
        elif self.state == FSM_RXM_Set.STATE.WAIT_GET_ACK:
            print("WAIT_GET_ACK->\n", obj)
            if isACK(obj):
                self._gottenObj.lpMode = self.lpMode
                manager.send(self._gottenObj.serialize())
                self.state = FSM_RXM_Set.STATE.WAIT_SET_ACK
            else:
                print("Ooops that went wrong")
                self.state = FSM_RXM_Set.STATE.DONE
        elif self.state == FSM_RXM_Set.STATE.WAIT_SET_ACK:
            print("WAIT_SET_ACK->\n", obj)
            if isACK(obj):
                self.state = FSM_RXM_Set.STATE.DONE
            else:
                print("Ooops that went wrong")
                self.state = FSM_RXM_Set.STATE.DONE
        else:
            print("HOW?->\n", obj)
            raise Exception("The FSM went boink.")


class Manager(UBXManager):
    def __init__(self, ser, debug=False):
        UBXManager.__init__(self, ser, debug)
        self._lock = Lock()
        self._dumpNMEA = True    # with _lock
        self._fsm = None         # with _lock
    def setDumpNMEA(self, val):
        with self._lock:
            self._dumpNMEA = val
        if self.debug:
            print("dumpNMEA={}".format(val))
    def onUBX(self, obj):
        with self._lock:
            if self._fsm is not None:
                self._fsm.onUBX(obj, manager)
                if self._fsm.done():
                    self._fsm = None
            else:
                print(obj)
    def onUBXError(self, msgClass, msgId, errMsg):
        print(msgClass, msgId, errMsg)
    def onNMEA(self, buffer):
        with self._lock:
            dump = self._dumpNMEA
        if dump:
            print(buffer)
    def done(self):
        with self._lock:
            return self._fsm is None
    def waitUntilDone(self, timeout=None):
        sleepTime = 0
        while not self.done():
            sleep(0.5)
            sleepTime += 0.5
            if timeout is not None and sleepTime > timeout:
                return False
        return True
    def getVER(self):
        msg = UBX.MON.VER.Get().serialize()
        with self._lock:
            self._fsm = FSM_VER_Get()
        self.send(msg)
    def setRXM(self, lpMode):
        msg = UBX.CFG.RXM.Get().serialize()
        with self._lock:
            self._fsm = FSM_RXM_Set(lpMode)
        self.send(msg)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Send UBX commands to u-blox M8 device.'
        )
    parser.add_argument(
        '--VER', dest='VER', action='store_true',
        help='Get the version string'
        )
    parser.add_argument(
        '--RXM', dest='RXM', action='store', type=int,
        help='Set the power mode (0=cont, 1=save)'
        )
    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true',
        help='Turn on debug mode'
        )
    args = parser.parse_args()

    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=None)
    debug = (os.environ.get("DEBUG") is not None) or args.debug

    manager = Manager(ser, debug=debug)
    manager.setDumpNMEA(False)  # turn off NMEA print
    if debug:
        sys.stderr.write("Starting UBXManager...\n")
    manager.start()

    sleep(1)

    if args.VER:
        manager.getVER()
        manager.waitUntilDone()

    if args.RXM is not None:
        manager.setRXM(args.RXM)
        manager.waitUntilDone()

    manager.shutdown()
    sys.exit(0)

    getVER = UBX.MON.VER.Get().serialize()
    setPMS = UBX.CFG.PMS.Set(powerSetupValue=2).serialize()
    getPMS = UBX.CFG.PMS.Get().serialize()
    getGNSS = UBX.CFG.GNSS.Get().serialize()
    getRXM = UBX.CFG.RXM.Get().serialize()

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
    sys.stderr.write("sending UBX.CFG.RXM.Get\n")
    manager.send(getRXM)

    sleep(2)
    manager.setDumpNMEA(True)

    manager.join()
