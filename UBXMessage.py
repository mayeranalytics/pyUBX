#!/usr/bin/env python3
"""TODO."""

import sys
import os
import serial
import threading
from enum import Enum
import struct
from time import sleep


class MessageClass(Enum):
    """UBX Class IDs."""

    NAV = b'\x01'  # Navigation Results Messages: Position, Speed, Time, Acceleration, Heading, DOP, SVs used
    RXM = b'\x02'  # Receiver Manager Messages: Satellite Status, RTC Status
    INF = b'\x04'  # Information Messages: Printf-Style Messages, with IDs such as Error, Warning, Notice
    ACK = b'\x05'  # Ack/Nak Messages: Acknowledge or Reject messages to CFG input messages
    CFG = b'\x06'  # Configuration Input Messages: Set Dynamic Model, Set DOP Mask, Set Baud Rate, etc.
    UPD = b'\x09'  # Firmware Update Messages: Memory/Flash erase/write, Reboot, Flash identification, etc.
    MON = b'\x0A'  # Monitoring Messages: Communication Status, CPU Load, Stack Usage, Task Status
    AID = b'\x0B'  # AssistNow Aiding Messages: Ephemeris, Almanac, other A-GPS data input
    TIM = b'\x0D'  # Timing Messages: Time Pulse Output, Time Mark Results
    ESF = b'\x10'  # External Sensor Fusion Messages: External Sensor Measurements and Status Information
    MGA = b'\x13'  # Multiple GNSS Assistance Messages: Assistance data for various GNSS
    LOG = b'\x21'  # Logging Messages: Log creation, deletion, info and retrieval
    SEC = b'\x27'  # Security Feature Messages
    HNR = b'\x28'  # High Rate Navigation Results Messages: High rate time, position, speed, heading


class UBXMessage(object):
    """Base class for UBX messages."""

    def __init__(self, msgClass, msgId, payload):
        """Instantiate UBXMessage from MessageClass, messageId and payload bytestring."""
        self.messageClass = msgClass
        self.messageId = msgId
        self.payload = payload

    def serialize(self):
        """Serialize the UBXMessage."""
        msg = struct.pack('cc', b'\xb5', b'\x62')
        msg += struct.pack('cc', self.messageClass.value, self.messageId)
        msg += struct.pack('<h', len(self.payload))
        msg += self.payload
        msg += struct.pack('>H', UBXMessage.Checksum(msg[2:]).get())
        sys.stderr.write("MSG: {}\n".format(msg))
        return msg

    class Checksum:
        """Incrementally calculate UBX message checksums."""

        def __init__(self, msg=None):
            """Instantiate object.

            If msg is not None calculate the checksum of the message, otherwise
            instantiate the checksums to zero.
            """
            self.reset()
            if msg is not None:
                for i in msg:
                    self.update(bytes([i]))

        def reset(self):
            """Reset the checksums to zero."""
            self.a = 0x00
            self.b = 0x00

        def update(self, byte):
            """Update checksums with byte."""
            i = ord(byte)
            self.a += i
            self.a &= 0xff
            self.b += self.a
            self.b &= 0xff

        def get(self):
            """Return the checksum (a 16-bit integer)."""
            return self.a * 256 + self.b


class UBX:
    """Comprises all message classes."""

    class MON:

        class VER:

            class Req(UBXMessage):
                def __init__(self):
                    UBXMessage.__init__(self, MessageClass.MON, b'\x04', b'')

            class Res(UBXMessage):
                def __init__(self):
                    UBXMessage.__init__(self, MessageClass.MON, b'\x04', b'')

    class CFG:

        class PMS:

            class Req(UBXMessage):
                def __init__(self):
                    UBXMessage.__init__(self, MessageClass.CFG, b'\x86', b'')

            class Res(UBXMessage):
                def __init__(self):
                    UBXMessage.__init__(self, MessageClass.CFG, b'\x86', b'')

            class Set(UBXMessage):
                def __init__(self, powerSetupValue=1, period=0, onTime=0):
                    payload = struct.pack(
                        '<BBhhBB', 0, powerSetupValue, period, onTime, 0, 0
                    )
                    UBXMessage.__init__(
                        self, MessageClass.CFG, b'\x86', payload
                    )

        class GNSS:

            class Req(UBXMessage):
                def __init__(self):
                    UBXMessage.__init__(self, MessageClass.CFG, b'\x3E', b'')


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


def format_byte_string(s):
    """Return a readable string of hex numbers."""
    return " ".join('{:02x}'.format(x) for x in s)


if __name__ == '__main__':

    # global variables!
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
