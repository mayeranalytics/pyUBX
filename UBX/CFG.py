"""Configuration Input Messages: Set Dynamic Model, Set DOP Mask, Set Baud Rate, etc."""

from UBXMessage import UBXMessage, initMessageClass
import struct


@initMessageClass
class CFG:
    """Message class CFG."""

    _class = 0x06

    class PMS:

        _id = 0x86

        def __init__(self, payload):
            pass

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

        def __init__(self, payload):
            pass

        class Get(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, CFG._class, CFG.GNSS._id, b'')
