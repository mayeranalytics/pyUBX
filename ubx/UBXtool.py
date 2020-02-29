#!/usr/bin/env python3
"""UBXTool is a command line app for sending and receiving UBX commands."""

import sys
import os
import serial
from time import sleep
from threading import Lock
from enum import Enum
import argparse
import datetime
from ubx.UBXManager import UBXManager
from ubx.FSM import *


@FSM_Get(UBX.MON.VER)
class FSM_VER_Get:
    pass


@FSM_Get(UBX.CFG.GNSS)
class FSM_GNSS_Get:
    pass


@FSM_Get(UBX.CFG.PMS)
class FSM_PMS_Get:
    pass


@FSM_Get(UBX.CFG.PM2)
class FSM_PM2_Get:
    pass


@FSM_Get(UBX.CFG.RATE)
class FSM_RATE_Get:
    pass


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
        print(obj)
        if self.state == FSM_RXM_Set.STATE.START:
            if isObj(obj, UBX.CFG.RXM):
                self._gottenObj = obj
                self.state = FSM_RXM_Set.STATE.WAIT_GET_ACK
            else:
                print("Didnt' get a UBX.CFG.RXM")
                self.state = FSM_RXM_Set.STATE.DONE
        elif self.state == FSM_RXM_Set.STATE.WAIT_GET_ACK:
            if isACK(obj):
                self._gottenObj.lpMode = self.lpMode
                manager.send(self._gottenObj.serialize())
                self.state = FSM_RXM_Set.STATE.WAIT_SET_ACK
            else:
                print("Ooops that went wrong, I was expecting an ACK")
                self.state = FSM_RXM_Set.STATE.DONE
        elif self.state == FSM_RXM_Set.STATE.WAIT_SET_ACK:
            if isACK(obj):
                self.state = FSM_RXM_Set.STATE.DONE
            else:
                print("Ooops that went wrong, I was expecting an ACK")
                self.state = FSM_RXM_Set.STATE.DONE
        else:
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
                self._fsm.onUBX(obj, self)
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
            print("{} {}".format(datetime.datetime.now().isoformat(), buffer))
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
    def VER_GET(self):
        msg = UBX.MON.VER.Get().serialize()
        with self._lock:
            self._fsm = FSM_VER_Get()
        self.send(msg)
    def GNSS_GET(self):
        msg = UBX.CFG.GNSS.Get().serialize()
        with self._lock:
            self._fsm = FSM_GNSS_Get()
        self.send(msg)
    def PMS_GET(self):
        msg = UBX.CFG.PMS.Get().serialize()
        with self._lock:
            self._fsm = FSM_PMS_Get()
        self.send(msg)
    def PM2_GET(self):
        msg = UBX.CFG.PM2.Get().serialize()
        with self._lock:
            self._fsm = FSM_PM2_Get()
        self.send(msg)
    def RATE_GET(self):
        msg = UBX.CFG.RATE.Get().serialize()
        with self._lock:
            self._fsm = FSM_RATE_Get()
        self.send(msg)
    def RXM_SET(self, lpMode):
        msg = UBX.CFG.RXM.Get().serialize()
        with self._lock:
            self._fsm = FSM_RXM_Set(lpMode)
        self.send(msg)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Send UBX commands to u-blox M8 device.'
        )
    parser.add_argument(
        '--VER-GET', dest='VER_GET', action='store_true',
        help='Get the version string'
        )
    parser.add_argument(
        '--GNSS-GET', dest='GNSS_GET', action='store_true',
        help='Get CFG-GNSS'
        )
    parser.add_argument(
        '--PMS-GET', dest='PMS_GET', action='store_true',
        help='Get CFG-PMS'
        )
    parser.add_argument(
        '--PM2-GET', dest='PM2_GET', action='store_true',
        help='Get CFG-PM2'
        )
    parser.add_argument(
        '--RATE-GET', dest='RATE_GET', action='store_true',
        help='Get CFG-RATE'
        )
    parser.add_argument(
        '--RXM', dest='RXM', action='store', type=int,
        help='Set the power mode (0=cont, 1=save)'
        )
    parser.add_argument(
        '--NMEA', dest='NMEA', action='store_true',
        help='Dump NMEA messages.'
        )
    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true',
        help='Turn on debug mode'
        )
    args = parser.parse_args()

    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=None)
    debug = (os.environ.get("DEBUG") is not None) or args.debug

    manager = Manager(ser, debug=debug)
    manager.setDumpNMEA(False)  # temporarily turn off NMEA print
    if debug:
        sys.stderr.write("Starting UBXManager...\n")
    manager.start()

    sleep(1)

    # do all getters
    for argName in filter(lambda s: s.endswith("_GET"), args.__dict__.keys()):
        if args.__dict__[argName]:
            getattr(manager, argName)()
            manager.waitUntilDone()

    if args.RXM is not None:
        manager.RXM_SET(args.RXM)
        manager.waitUntilDone()

    if args.NMEA:
        manager.setDumpNMEA(True)
        manager.join()
    else:
        manager.shutdown()
        sys.exit(0)

    sys.exit(1)
