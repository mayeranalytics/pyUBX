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


def format_byte_string(s):
    """Return a readable string of hex numbers."""
    return " ".join('{:02x}'.format(x) for x in s)
