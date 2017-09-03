#!/usr/bin/env python3
"""TODO."""

import sys
import os
import serial
import threading
from enum import Enum
import struct
from time import sleep
from UBXMessage import UBXMessage, format_byte_string


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

    def __init__(self, ser):
        """Instantiate with serial."""
        threading.Thread.__init__(self)
        self.ser = ser
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
        logfile = open("UBX.log", "wb")
        self._reset()
        while True:
            byte = self.ser.read(1)
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
            self.onNMEA(self.buffer.decode('ascii'))
        else:
            self.onNMEAError(
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
            self.onUBX(self.ubx_class, self.ubx_id, self.buffer)
        else:
            self.onUBXError(
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

    def onNMEA(self, buffer):
        """Handle an NMEA message."""
        print("NMEA: {}".format(buffer))

    def onNMEAError(self, errMsg):
        """Handle an NMEA error."""
        print("NMEA ERR: {}".format(errMsg))

    def onUBX(self, msgClass, msgId, buffer):
        """Handle an UBX message."""
        print("UBX: {:02X}:{:02X} len={} payload={}".format(
            msgClass, msgId, len(buffer), format_byte_string(buffer)))

    def onUBXError(self, msgClass, msgId, errMsg):
        """Handle an UBX error."""
        m = struct.pack('cc', bytes([msgClass]), bytes([msgId]))
        m += struct.pack('<h', len(self.buffer))
        m += self.buffer
        print("UBX ERR {:02X}/{:02X}: {} payload={}"
              .format(msgClass, msgId, errMsg, format_byte_string(m)))

    def send(self, msg):
        """Send message to ser."""
        print("SEND: {}".format(format_byte_string(msg)))
        self.ser.write(msg)
