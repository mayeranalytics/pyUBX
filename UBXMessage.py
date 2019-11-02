#!/usr/bin/env python3
"""TODO."""

import struct
import inspect
from enum import Enum
import sys
from itertools import accumulate


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


def _byte(i):
    """Helper function: convert int 0..255 to bytestring byte."""
    return bytes([i])


class UBXMessage(object):
    """Base class for UBX messages."""

    sync_char_1 = b'\xb5'
    sync_char_2 = b'\x62'

    def __init__(self, msgClass, msgId, payload):
        """Instantiate UBXMessage from MessageClass, messageId and payload.

        msgClass and msgId should be ints.
        """
        self._class = msgClass
        self._id = msgId
        self._payload = payload

    @staticmethod
    def make(msgClass, msgId, payload):
        """Return a proper UBX message from the given class, id and payload."""
        msg = struct.pack('cc', UBXMessage.sync_char_1, UBXMessage.sync_char_2)
        msg += struct.pack('cc', _byte(msgClass), _byte(msgId))
        msg += struct.pack('<h', len(payload))
        msg += payload
        msg += struct.pack('>H', UBXMessage.Checksum(msg[2:]).get())
        return msg

    @staticmethod
    def extract(msg):
        """Return msgClass, msgId, payload from given message.

        This is the inverse of make(), used mostly for debugging purposes.
        """
        (sync1, sync2) = struct.unpack('cc', msg[0:2])
        if sync1 != UBXMessage.sync_char_1 or sync2 != UBXMessage.sync_char_2:
            raise Exception("Sync chars not correct.")
        msgClass, msgId = struct.unpack('cc', msg[2:4])
        lenPayload = struct.unpack('<h', msg[4:6])[0]
        payload = msg[6:(6+lenPayload)]
        trueCksum = UBXMessage.Checksum(msg[2:(len(msg)-2)]).get()
        msgCksum = struct.unpack('>H', msg[6+lenPayload:])[0]
        if trueCksum != msgCksum:
            raise Exception(
                "Calculated checksum 0x{:02x} does not match 0x{:02x}."
                .format(msgCksum, trueCksum)
                )
        return ord(msgClass), ord(msgId), payload

    def serialize(self):
        """Serialize the UBXMessage."""
        return UBXMessage.make(self._class, self._id, self._payload)

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


def _mkFieldInfo(Fields):
    # The following is a list of (name, formatChar) tuples, such as
    # [(1, 'clsID', U1), (2, 'msgID', U1)]
    once = [
        (v.ord, k, v)
        for k, v in Fields.__dict__.items()
        if not k.startswith('__') and k != 'Repeated'
    ]
    once.sort()
    repeated = Fields.__dict__.get('Repeated')
    repeated = [] if repeated is None else _mkFieldInfo(repeated)
    return {
        'once': ([v for (o, k, v) in once],    # list of types
                 [k for (o, k, v) in once]),   # list of var names
        'repeat': repeated
        }


def _mkNamesAndTypes(fieldInfo, msgLength):
    """Make list of variable names and list of variable types.

    Input is the fieldInfo as returned by _mkFieldInfo.
    The number of repeated objects is deduced from the message length and
    the types of variables in the 'once' and 'repeat' block of the input."""
    varTypes, varNames = fieldInfo['once']
    repeat = fieldInfo['repeat']
    if repeat:
        varTypesRepeat, varNamesRepeat = repeat['once']     # nest level 1 only
        sizeOnce = sum([t._size for t in varTypes])
        sizeRepeat = sum([t._size for t in varTypesRepeat])
        N = (msgLength - sizeOnce) // sizeRepeat
        sizeTotal = sizeOnce + N * sizeRepeat
        if sizeTotal != msgLength:
            errmsg = "message length {} does not match {}"\
                     .format(msgLength, sizeTotal)
            raise Exception(errmsg)
        varTypes += N * varTypesRepeat
        varNames += _flatten(list(
            map(lambda i: list(map(lambda s: s+"_"+str(i),
                                   varNamesRepeat)
                              ),
                range(1, N+1))
            )
        )
    return varNames, varTypes


def _flatten(l):
    return [item for sublist in l for item in sublist]


def initMessageClass(cls):
    """Decorator for the python class representing a UBX message class.

    It does the following in cls:
    - add a dict with name _lookup that maps UBX message ID to python subclass.
    In each subclass it does this:
    - add an __init__ if it doesn't exist
    - add a __str__ if it doesn't exist
    Function __init__ instantiates the object from a message.
    Function __str__ creates a human readable string from the object.
    """
    cls_name = cls.__name__
    subClasses = [c for c in cls.__dict__.values() if type(c) == type]

    lookup = dict([(getattr(subcls, '_id'), subcls) for subcls in subClasses])
    setattr(cls, "_lookup", lookup)

    for sc in subClasses:
        if sc.__dict__.get('Fields') is None:       # 'Fields' must be present
            raise Exception(
                "Class {}.{} has no Fields"
                .format(cls.__name__, sc.__name__)
            )
        # add __init__ to subclass if necessary
        if sc.__dict__.get('__init__') is None:
            def __init__(self, msg):
                """Instantiate object from message bytestring."""
                fieldInfo = _mkFieldInfo(self.Fields)
                varNames, varTypes = _mkNamesAndTypes(fieldInfo, len(msg))
                if not varNames:
                    errmsg = 'No variables found in UBX.{}.{}.'\
                             .format(cls_name, sc.__name__)
                    errmsg += ' Is the \'Fields\' class empty?'
                    raise Exception(errmsg)
                _len = len(msg)     # msg will be consumed in the loop
                for (varName, varType) in zip(varNames, varTypes):
                    val, msg = varType.parse(msg)
                    setattr(self, varName, val)
                if len(msg) != 0:
                    clsName = "UBX.{}.{}".format(cls_name, sc.__name__)
                    raise Exception(
                        "Message not fully consumed while parsing a {}!"
                        .format(clsName)
                    )
                self._len = _len
                self._payload = msg
            setattr(sc, "__init__", __init__)
        # add __str__ to subclass if necessary
        if sc.__dict__.get('__str__') is None:
            def __str__(self):
                """Return human readable string."""
                fieldInfo = _mkFieldInfo(self.Fields)
                varNames, varTypes = _mkNamesAndTypes(fieldInfo, self._len)
                s = "{}-{}:".format(cls_name, type(self).__name__)
                for (varName, varType) in zip(varNames, varTypes):
                    s += "\n  {}={}".format(
                        varName,
                        varType.toString(getattr(self, varName))    # prettify
                        )
                return s
            setattr(sc, "__str__", __str__)
        # add serialize to subclass if necessary
        if sc.__dict__.get('serialize') is None:
            def serialize(self):
                """UBX-serialize this object."""
                fieldInfo = _mkFieldInfo(self.Fields)
                varNames, varTypes = _mkNamesAndTypes(fieldInfo, self._len)
                payload = b''
                for name, typ in zip(varNames, varTypes):
                    val = getattr(self, name)
                    payload += typ.serialize(val)
                return UBXMessage.make(
                    self._class, self._id, payload
                    )
            setattr(sc, "serialize", serialize)
        # set the '_class' class variable in subclass
        setattr(sc, '_class', cls._class)
    return cls


def classFromMessageClass():
    """Look up the python class corresponding to a UBX message class.

    The result is something like
    [(5, UBX.ACK.ACK), (6, UBX.CFG.CFG), (10, UBX.MON.MON)]
    """
    return dict([
        (getattr(v, '_class'), v)
        for (k, v) in inspect.getmembers(sys.modules["UBX"], inspect.isclass)
        if v.__name__ not in [
            "UBXMessage", "U1", "I1", "X1", "U2", "I2", "X2",
            "U4", "I4", "X4", "R4", "R8", "CH", "U"
            ]
    ])


def parseUBXPayload(msgClass, msgId, payload):
    """Parse a UBX payload from message class, message ID and payload."""
    Cls = classFromMessageClass().get(msgClass)
    if Cls is None:
        err = "Cannot parse message class {}.\n Available: {}"\
              .format(msgClass, classFromMessageClass())
        raise Exception(err)
    Subcls = Cls._lookup.get(msgId)
    if Subcls is None:
        raise Exception(
            "Cannot parse message ID {} of message class {}.\n Available: {}"
            .format(msgId, msgClass, Cls._lookup))
    return Subcls(payload)


def parseUBXMessage(msg):
    """Parse a UBX message."""
    msgClass, msgId, payload = UBXMessage.extract(msg)
    return parseUBXPayload(msgClass, msgId, payload)


def formatByteString(s):
    """Return a readable string of hex numbers."""
    return " ".join('{:02x}'.format(x) for x in s)


def addGet(cls):
    """Decorator that adds a Get function to the subclass."""
    class Get(UBXMessage):
        def __init__(self):
            # this only works because class and module have the same name!
            import UBX
            _class = eval(cls.__module__)._class
            UBXMessage.__init__(self, _class, cls._id, b'')
    setattr(cls, "Get", Get)
    return cls
