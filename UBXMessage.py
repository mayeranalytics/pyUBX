#!/usr/bin/env python3
"""TODO."""

import struct
import inspect
from enum import Enum
import sys
import UBX


class MessageClass(Enum):
    """UBX Class IDs."""

    NAV = b'\x01'  # Navigation Results Messages: Position, Speed, Time, Acceleration, Heading, DOP, SVs used
    RXM = b'\x02'  # Receiver Manager Messages: Satellite Status, RTC Status
    INF = b'\x04'  # Information Messages: Printf-Style Messages, with IDs such as Error, Warning, Notice
    UPD = b'\x09'  # Firmware Update Messages: Memory/Flash erase/write, Reboot, Flash identification, etc.
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
        self.messageClass = bytes([msgClass])
        self.messageId = bytes([msgId])
        self.payload = payload

    def serialize(self):
        """Serialize the UBXMessage."""
        msg = struct.pack('cc', b'\xb5', b'\x62')
        msg += struct.pack('cc', self.messageClass, self.messageId)
        msg += struct.pack('<h', len(self.payload))
        msg += self.payload
        msg += struct.pack('>H', UBXMessage.Checksum(msg[2:]).get())
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
            self.a, self.b = 0x00, 0x00

        def update(self, byte):
            """Update checksums with byte."""
            i = ord(byte)
            self.a += i
            self.a &= 0xff
            self.b += self.a
            self.b &= 0xff

        def get(self):
            """Return the checksum (a 16-bit integer, ck_a is the MSB)."""
            return self.a * 256 + self.b


def initMessageClass(cls):
    """Decorator for the python class representing a UBX message class.

    It adds a dict with name '_lookup' that maps UBX message ID to python
    subclass.
    """
    cls_name = cls.__name__
    subClasses = [c for c in cls.__dict__.values() if type(c) == type]
    # 1. add lookup
    lookup = dict([(getattr(subcls, '_id'), subcls) for subcls in subClasses])
    setattr(cls, "_lookup", lookup)
    # 2. add __init__ and __str__ in each subclass (if it doesn't exist)
    for sc in subClasses:
        if sc.__dict__.get('Fields') is None:
            raise Exception(
                "Class {}.{} has no Fields"
                .format(cls.__name__, sc.__name__)
            )
        if sc.__dict__.get('__init__') is None:
            def __init__(self, msg):
                # The following is a list of (name, formatChar) tuples, such as
                # [('clsID', 'B'), ('msgID', 'B')]
                defStructPack = [
                    (k, v.typ)
                    for k, v in self.Fields.__dict__.items()
                    if not k.startswith('__')
                ]
                packFmt = "".join([fmt for _, fmt in defStructPack])
                values = struct.unpack(packFmt, msg)
                for (i, (name, formatChar)) in enumerate(defStructPack):
                    setattr(self, name, values[i])
            setattr(sc, "__init__", __init__)
        if sc.__dict__.get('__str__') is None:
            def __str__(self):
                # The following is a list of (name, formatChar) tuples, such as
                # [('clsID', 'B'), ('msgID', 'B')]
                defStructPack = [
                    (k, v.typ)
                    for k, v in self.Fields.__dict__.items()
                    if not k.startswith('__')
                ]
                sc_name = type(self).__name__
                s = "{}-{}".format(cls_name, sc_name)
                for name, formatChar in defStructPack:
                    s += "\n  {}={}".format(name, getattr(self, name))
                return s
            setattr(sc, "__str__", __str__)
    return cls


def classFromMessageClass():
    """Look up the python class corresponding to a UBX message class.

    The result is something like
    [(5, UBX.ACK.ACK), (6, UBX.CFG.CFG), (10, UBX.MON.MON)]
    """
    return dict([
        (getattr(v, '_class'), v)
        for (k, v) in inspect.getmembers(sys.modules["UBX"], inspect.isclass)
        if v.__name__ not in ["UBXMessage", "U1"]
    ])


def parseUBXMessage(msgClass, msgId, payload):
    """Parse a UBX message from message class, message ID and payload."""
    Cls = classFromMessageClass().get(msgClass)
    if Cls is None:
        raise Exception("Cannot parse message class {}".format(msgClass))
    Subcls = Cls._lookup.get(msgId)
    if Subcls is None:
        raise Exception("Cannot parse message ID {} of message class {}"
                        .format(msgId, msgClass.__name__))
    return Subcls(payload)


def formatByteString(s):
    """Return a readable string of hex numbers."""
    return " ".join('{:02x}'.format(x) for x in s)


def stringFromByteString(bs):
    """Extract a null-terminated string from bytestring."""
    i = bs.find(0)
    if i < 0:
        return ""
    else:
        return bs[0:i].decode('ascii')
