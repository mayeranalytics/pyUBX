"""Define all types here.

Each type must have a variable typ and ord.
- typ: Contains the python struct packing letter
- ord: Contains a sequential ordering number
"""

from struct import Struct, unpack

# Note: All classes listed here must be also listed in UBXMessages.py,
# function classFromMessageClass !!


def _InitType(cls):
    """Add the standard __init__ to the class."""
    # 1. add __init__ function to cls
    if cls.__dict__.get('__init__') is None:
        def __init__(self, _ord):
            self.ord = _ord
        setattr(cls, '__init__', __init__)
    # 2. add parse function to cls
    if cls.__dict__.get('parse') is None:
        def parse(self, msg):
            if len(msg) < self._size:
                err = "Message length {} is shorter than required {}"\
                      .format(len(msg), self._size)
                raise Exception(err)

            val = unpack(self.fmt, msg[0:self._size])[0]
            return val, msg[self._size:]
        setattr(cls, "parse", parse)
    # 3. add _size variable to cls
    if cls.__dict__.get('_size') is None:
        setattr(cls, '_size', Struct(cls.fmt).size)
    # 4. add toString static method
    if cls.__dict__.get('toString') is None:
        @staticmethod
        def toString(val):
            return ("0x{:0" + str(cls._size*2) + "X}")\
                   .format(val)
        setattr(cls, 'toString', toString)
    return cls


def stringFromByteString(bs):
    """Extract a null-terminated string from bytestring."""
    i = bs.find(0)
    return "" if i < 0 else bs[0:i].decode('ascii')


@_InitType
class U1:
    """UBX Unsigned Char."""
    fmt   = "B"
    ctype = "uint8_t"

@_InitType
class I1:
    """UBX Signed Char."""
    fmt   = "b"
    ctype = "int8_t"

@_InitType
class X1:
    """UBX 1-byte bitfield."""
    fmt   = "B"
    ctype = "uint8_t"

@_InitType
class U2:
    """UBX Unsigned Short."""
    fmt   = "H"
    ctype = "uint16_t"

@_InitType
class I2:
    """UBX Signed Short."""
    fmt   = "h"
    ctype = "int16_t"

@_InitType
class X2:
    """UBX 2-byte bitfield."""
    fmt   = "H"
    ctype = "uint16_t"

@_InitType
class U4:
    """UBX Unsigned Int."""
    fmt   = "I"
    ctype = "uint32_t"

@_InitType
class I4:
    """UBX Signed Int."""
    fmt   = "i"
    ctype = "int32_t"

@_InitType
class X4:
    """UBX 4-byte bitfield."""
    fmt   = "I"
    ctype = "uint32_t"

@_InitType
class R4:
    """UBX single precision float."""
    fmt   = "f"
    ctype = "float"

@_InitType
class R8:
    """UBX double precision float."""
    fmt   = "d"
    ctype = "double"

class CH:
    """ASCII / ISO 8859.1 Encoding."""
    def __init__(self, _ord, N, nullTerminatedString=False):
        self.N = N
        self.fmt = None  # it isn't needed
        self.ord = _ord
        self._size = N
        self.ctype = "char[{}]".format(N)
        self._nullTerminatedString = nullTerminatedString
    def parse(self, msg):
        if len(msg) < self.N:
            err = "Message length {} is shorter than required {}"\
                  .format(len(msg), self._size)
            raise Exception(err)
        val = msg[0:self._size]
        if self._nullTerminatedString:
            val = stringFromByteString(val)
        return val, msg[self._size:]
    @staticmethod
    def toString(val):
        return '"{}"'.format(val)
