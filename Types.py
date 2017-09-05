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
    def ctype(): return "uint8_t"

@_InitType
class I1:
    """UBX Signed Char."""
    fmt   = "b"
    def ctype(): return "int8_t"

@_InitType
class X1:
    """UBX 1-byte bitfield."""
    fmt   = "B"
    def ctype(): return "uint8_t"

@_InitType
class U2:
    """UBX Unsigned Short."""
    fmt   = "H"
    def ctype(): return "uint16_t"

@_InitType
class I2:
    """UBX Signed Short."""
    fmt   = "h"
    def ctype(): return "int16_t"

@_InitType
class X2:
    """UBX 2-byte bitfield."""
    fmt   = "H"
    def ctype(): return "uint16_t"

@_InitType
class U4:
    """UBX Unsigned Int."""
    fmt   = "I"
    def ctype(): return "uint32_t"

@_InitType
class I4:
    """UBX Signed Int."""
    fmt   = "i"
    def ctype(): return "int32_t"

@_InitType
class X4:
    """UBX 4-byte bitfield."""
    fmt   = "I"
    def ctype(): return "uint32_t"

@_InitType
class R4:
    """UBX single precision float."""
    fmt   = "f"
    def ctype(): return "float"

@_InitType
class R8:
    """UBX double precision float."""
    fmt   = "d"
    def ctype(): return "double"

class CH:
    """ASCII / ISO 8859.1 Encoding."""
    fmt = None  # Not needed
    def __init__(self, _ord, N, nullTerminatedString=False):
        self.N = N
        self.ord = _ord
        self._size = N
        self._nullTerminatedString = nullTerminatedString
    def ctype(): return "char[{}]".format(self.N)
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

class U:
    """Variable-length array of unsigned chars."""
    fmt = None  # Not needed
    def ctype(): return "uint8_t[{}]".format(self.N)
    def __init__(self, _ord, N):
        self._ord = _ord
        self.N = N
    def parse(self, msg):
        if len(msg) < self.N:
            err = "Message length {} is shorter than required {}"\
                  .format(len(msg), self._size)
            raise Exception(err)
        val = msg[0:self._size]]
        return val, msg[self._size:]
    @staticmethod
    def toString(val):
        return '"{}"'.format(val)
