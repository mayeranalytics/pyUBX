#!/usr/bin/env python3
"""TODO."""

import threading
from enum import Enum
import struct


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

    def __init__(self, ser, debug=False):
        """Instantiate with serial."""
        from UBXMessage import UBXMessage
        threading.Thread.__init__(self)
        self.ser = ser
        self.debug = debug
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
            logfile = open("UBX.log", "wb")
        self._reset()
        while True:
            byte = self.ser.read(1)
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
        from UBXMessage import parseUBXMessage, formatByteString
        try:
            obj = parseUBXMessage(msgClass, msgId, buffer)
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
        from UBXMessage import formatByteString
        print("SEND: {}".format(formatByteString(msg)))
        self.ser.write(msg)
