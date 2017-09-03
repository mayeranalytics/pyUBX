"""Configuration Input Messages: Set Dynamic Model, Set DOP Mask, Set Baud Rate, etc."""

from UBXMessage import UBXMessage, initMessageClass
import struct
from Types import U1, U2


@initMessageClass
class CFG:
    """Message class CFG."""

    _class = 0x06

    class PMS:

        _id = 0x86

        class Fields:
            version = U1()
            powerSetupValue = U1()
            period = U2()
            onTime = U2()
            reserved = U2()

        class Get(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, CFG._class, CFG.PMS._id, b'')

        class Set(UBXMessage):
            def __init__(self, powerSetupValue=1, period=0, onTime=0):
                payload = struct.pack(
                    '<BBhhBB', 0, powerSetupValue, period, onTime, 0, 0
                )
                UBXMessage.__init__(
                    self, CFG._class, CFG.PMS._id, payload
                )

    class GNSS:

        _id = 0x3E

        class Fields:
            pass

        class Get(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, CFG._class, CFG.GNSS._id, b'')
