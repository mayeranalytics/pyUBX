"""Define all types here."""

# Note: All classes listed here must be also listed in UBXMessages.py,
# function classFromMessageClass !!

class U1:
    """UBX Unsigned Char."""
    typ = "B"

class I1:
    """UBX Signed Char."""
    typ = "b"

class X1:
    """UBX 1-byte bitfield."""
    typ = "B"

class U2:
    """UBX Unsigned Short."""
    typ = "H"

class I2:
    """UBX Signed Short."""
    typ = "h"

class X2:
    """UBX 2-byte bitfield."""
    typ = "H"

class U4:
    """UBX Unsigned Int."""
    typ = "I"

class I4:
    """UBX Signed Int."""
    typ = "i"

class X4:
    """UBX 4-byte bitfield."""
    typ = "H"

class R4:
    """UBX single precision float."""
    typ = "f"

class R8:
    """UBX double precision float."""
    typ = "d"

class CH:
    """ASCII / ISO 8859.1 Encoding."""
    def __init__(self, N):
        self.N = N
        self.typ = "B" * N
