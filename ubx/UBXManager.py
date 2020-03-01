#!/usr/bin/env python3
"""TODO."""

import threading
from enum import Enum
import sys
from queue import Queue
from ubx import UBXMessage
import time


class UBXManager(threading.Thread):
    """The NMEA/UBX reader/writer thread."""

    class STATE(Enum):
        START = 0
        NMEA_BODY = 1
        NMEA_CHKSUM_1 = 2
        NMEA_CHKSUM_2 = 3
        UBX_SYNC_CHAR_2 = 4
        UBX_CLASS = 5
        UBX_ID = 6
        UBX_LENGTH_1 = 7
        UBX_LENGTH_2 = 8
        UBX_PAYLOAD = 9
        UBX_CHKSUM_1 = 10
        UBX_CHKSUM_2 = 11

    def __init__(self, ser, debug=False, eofTimeout=None):
        """Instantiate with serial.

        :param ser: serial port, file, or other object that supports ser.read(1)
        :param debug: write to log.   (filename, or if True, default to ./UBX.log)
        :param eofTimeout:  seconds to wait for more bytes on read.  Default None->keep trying
        """
        threading.Thread.__init__(self)
        self.ser = ser
        self.debug = debug
        self.eofTimeout = eofTimeout
        self._shutDown = False
        self.ubx_chksum = UBXMessage.Checksum()

    def run(self):
        """Run the parser."""
        transitionFrom = [
            self._fromSTART,
            self._fromNMEA_BODY,
            self._fromNMEA_CHKSUM_1,
            self._fromNMEA_CHKSUM_2,
            self._fromUBX_SYNC_CHAR_2,
            self._fromUBX_CLASS,
            self._fromUBX_ID,
            self._fromUBX_LENGTH_1,
            self._fromUBX_LENGTH_2,
            self._fromUBX_PAYLOAD,
            self._fromUBX_CHKSUM_1,
            self._fromUBX_CHKSUM_2,
        ]
        if self.debug:
            debugfile = "UBX.log" if self.debug is True else self.debug
            logfile = open(debugfile, "wb")
            sys.stderr.write("Writing log to {}\n".format(debugfile))
        self._reset()
        while not self._shutDown:
            if hasattr(self.ser, 'read'):
                byte = self.ser.read(1)
                if len(byte) == 0:
                    if self.eofTimeout is None:
                        time.sleep(0.01)    # Sleep 10 ms so at least it is not just busy-waiting
                        continue
                    else:
                        time.sleep(self.eofTimeout)
                        byte = self.ser.read(1)
                        if len(byte) == 0:
                            break   # Still nothing.  Done
            else:
                byte = self.ser.recv(1)
            if self.debug:
                logfile.write(byte)
                logfile.flush()
            self.state = transitionFrom[self.state.value](byte)

    def _reset(self):
        self.buffer = b''
        self.chksum = 0
        self.chksum_calc = 0
        self.ubx_class = 0
        self.ubx_id = 0
        self.ubx_length = 0
        self.state = UBXManager.STATE.START
        self.ubx_chksum.reset()

    def _fromSTART(self, byte):
        if byte == b'$':
            return UBXManager.STATE.NMEA_BODY
        elif byte == b'\xb5':
            return UBXManager.STATE.UBX_SYNC_CHAR_2
        else:
            return UBXManager.STATE.START

    def _fromNMEA_BODY(self, byte):
        if byte == b'*':
            return UBXManager.STATE.NMEA_CHKSUM_1
        else:
            self.buffer += byte
            self.chksum_calc ^= ord(byte)
            return UBXManager.STATE.NMEA_BODY

    def _fromNMEA_CHKSUM_1(self, byte):
        try:
            self.chksum = int(byte, 16) * 16
        except ValueError:
            return UBXManager.STATE.START
        return UBXManager.STATE.NMEA_CHKSUM_2

    def _fromNMEA_CHKSUM_2(self, byte):
        try:
            self.chksum += int(byte, 16)
        except ValueError:
            return UBXManager.STATE.START
        if self.chksum == self.chksum_calc:
            self._onNMEA(self.buffer.decode('ascii'))
        else:
            self._onNMEAError(
                "Incorrect Checksum: {:02X} should be {:02X}"
                .format(self.chksum_calc, self.chksum)
            )
        self._reset()
        return UBXManager.STATE.START

    def _fromUBX_SYNC_CHAR_2(self, byte):
        if byte == b'\x62':
            return UBXManager.STATE.UBX_CLASS
        else:
            return UBXManager.STATE.START

    def _fromUBX_CLASS(self, byte):
        self.ubx_class = ord(byte)
        self.ubx_chksum.update(byte)
        return UBXManager.STATE.UBX_ID

    def _fromUBX_ID(self, byte):
        self.ubx_id = ord(byte)
        self.ubx_chksum.update(byte)
        return UBXManager.STATE.UBX_LENGTH_1

    def _fromUBX_LENGTH_1(self, byte):
        self.ubx_length = ord(byte)
        self.ubx_chksum.update(byte)
        return UBXManager.STATE.UBX_LENGTH_2

    def _fromUBX_LENGTH_2(self, byte):
        self.ubx_length = self.ubx_length + 256 * ord(byte)
        self.ubx_chksum.update(byte)
        return UBXManager.STATE.UBX_PAYLOAD

    def _fromUBX_PAYLOAD(self, byte):
        if self.ubx_length > 0:
            self.buffer += byte
            self.ubx_length -= 1
            self.ubx_chksum.update(byte)
            return UBXManager.STATE.UBX_PAYLOAD
        else:
            self.chksum = 256 * ord(byte)   # CK_A shifted left
            return UBXManager.STATE.UBX_CHKSUM_1

    def _fromUBX_CHKSUM_1(self, byte):
        self.chksum += ord(byte)  # 256 * CK_A + CK_B
        return UBXManager.STATE.UBX_CHKSUM_2

    def _fromUBX_CHKSUM_2(self, byte):
        if self.chksum == self.ubx_chksum.get():
            self._onUBX(self.ubx_class, self.ubx_id, self.buffer)
        else:
            self._onUBXError(
                self.ubx_class,
                self.ubx_id,
                "Incorrect Checksum: {:04X} should be {:04X}"
                    .format(self.ubx_chksum.get(), self.chksum)
            )
        self._reset()
        if byte == b'$':
            return UBXManager.STATE.NMEA_BODY
        elif byte == b'\xb5':
            return UBXManager.STATE.UBX_SYNC_CHAR_2
        else:
            return UBXManager.STATE.START

    def _onNMEA(self, buffer):
        self.onNMEA(buffer)

    def onNMEA(self, buffer):
        """Default handler for good NMEA message."""
        print("NMEA: {}".format(buffer))

    def _onNMEAError(self, errMsg):
        self.onNMEAError(errMsg)

    def onNMEAError(self, errMsg):
        """Default handler for faulty NMEA message."""
        print("NMEA ERR: {}".format(errMsg))

    def _onUBX(self, msgClass, msgId, buffer):
        from ubx.UBXMessage import parseUBXPayload, formatByteString
        try:
            obj = parseUBXPayload(msgClass, msgId, buffer)
        except Exception as e:
            errMsg = "No parse, \"{}\", payload={}".format(
                     e, formatByteString(buffer))
            self.onUBXError(msgClass, msgId, errMsg)
        else:
            self.onUBX(obj)

    def onUBX(self, obj):
        """Default handler for good UBX message."""
        print(obj)

    def _onUBXError(self, msgClass, msgId, errMsg):
        """Handle an UBX error."""

    def onUBXError(self, msgClass, msgId, errMsg):
        """Default handler for faulty or not yet defined UBX message."""
        print("UBX ERR {:02X}:{:02X} {}"
              .format(msgClass, msgId, errMsg))

    def send(self, msg):
        """Send message to ser."""
        from ubx.UBXMessage import formatByteString
        if self.debug:
            print("SEND: {}".format(formatByteString(msg)))
        if hasattr(self.ser, 'write'):
            self.ser.write(msg)
        else:
            self.ser.send(msg)

    def shutdown(self):
        """Stop the manger."""
        self._shutDown = True


class UBXQueue(UBXManager):
    """UBX Mananger that puts good UBX messages on queue

    Use .empty() and .get() as for a queue.Queue
    """

    def __init__(self, ser, debug=False, start=False, eofTimeout=None, queue=None):
        """
        :param ser: Passed to UBXManager
        :param eofTimeout: Passed to UBXManager
        :param start: start thread immediately on init
        :param queue: Optional queue to use, otherwise uses own
        """
        self._queue = queue if queue else Queue()
        # Reflects the has-a queue's get() and empty() methods
        self.get = self._queue.get
        self.empty = self._queue.empty
        super(UBXQueue, self).__init__(ser=ser, debug=debug, eofTimeout=eofTimeout)
        if start:
            self.start()

    def onUBX(self, obj):  # handle good UBX message
        self._queue.put(obj)

    def join(self):
        super(UBXQueue, self).join()
        self._queue.join()
