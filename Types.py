"""Define all types here.

Each type must have a variable typ and ord.
- typ: Contains the python struct packing letter
- ord: Contains a sequential ordering number
"""

from struct import Struct

# Note: All classes listed here must be also listed in UBXMessages.py,
# function classFromMessageClass !!


def _Init(cls):
    """Add the standard __init__ to the class."""
    def __init__(self, _ord):
        self.ord = _ord
    setattr(cls, '__init__', __init__)
    setattr(cls, '_size', Struct(cls.fmt).size)
    return cls


@_Init
class U1:
    """UBX Unsigned Char."""
    fmt = "B"
    ctype = "uint8_t"

@_Init
class I1:
    """UBX Signed Char."""
    fmt = "b"
    ctype = "int8_t"

@_Init
class X1:
    """UBX 1-byte bitfield."""
    fmt = "B"
    ctype = "uint8_t"

@_Init
class U2:
    """UBX Unsigned Short."""
    fmt = "H"
    ctype = "uint16_t"

@_Init
class I2:
    """UBX Signed Short."""
    fmt = "h"
    ctype = "int16_t"

@_Init
class X2:
    """UBX 2-byte bitfield."""
    fmt = "H"
    ctype = "uint16_t"

@_Init
class U4:
    """UBX Unsigned Int."""
    fmt = "I"
    ctype = "uint32_t"

@_Init
class I4:
    """UBX Signed Int."""
    fmt = "i"
    ctype = "int32_t"

@_Init
class X4:
    """UBX 4-byte bitfield."""
    fmt = "I"
    ctype = "uint32_t"

@_Init
class R4:
    """UBX single precision float."""
    fmt = "f"
    ctype = "float"

@_Init
class R8:
    """UBX double precision float."""
    fmt = "d"
    ctype = "double"

class CH:
    """ASCII / ISO 8859.1 Encoding."""
    def __init__(self, _ord, N):
        self.N = N
        self.fmt = "B" * N
        self.ord = _ord
        self._size = N
        self.ctype = "char[{}]".format(N)
