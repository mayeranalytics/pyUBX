"""Define all types here.

Each type must have a variable typ and ord.
- typ: Contains the python struct packing letter
- ord: Contains a sequential ordering number
"""

# Note: All classes listed here must be also listed in UBXMessages.py,
# function classFromMessageClass !!


def _Init(cls):
    """Add the standard __init__ to the class."""
    def __init__(self, ord):
        self.ord = ord
    setattr(cls, '__init__', __init__)
    return cls


@_Init
class U1:
    """UBX Unsigned Char."""
    typ = "B"

@_Init
class I1:
    """UBX Signed Char."""
    typ = "b"

@_Init
class X1:
    """UBX 1-byte bitfield."""
    typ = "B"

@_Init
class U2:
    """UBX Unsigned Short."""
    typ = "H"

@_Init
class I2:
    """UBX Signed Short."""
    typ = "h"

@_Init
class X2:
    """UBX 2-byte bitfield."""
    typ = "H"

@_Init
class U4:
    """UBX Unsigned Int."""
    typ = "I"

@_Init
class I4:
    """UBX Signed Int."""
    typ = "i"

@_Init
class X4:
    """UBX 4-byte bitfield."""
    typ = "I"

@_Init
class R4:
    """UBX single precision float."""
    typ = "f"

@_Init
class R8:
    """UBX double precision float."""
    typ = "d"

class CH:
    """ASCII / ISO 8859.1 Encoding."""
    def __init__(self, ord, N):
        self.N = N
        self.typ = "B" * N
        self.ord = ord
