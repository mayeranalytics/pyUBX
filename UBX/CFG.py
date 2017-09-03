from UBXMessage import UBXMessage, MessageClass
import struct


class CFG:
    """Message class CFG."""

    class PMS:

        class Req(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, MessageClass.CFG, b'\x86', b'')

        class Res(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, MessageClass.CFG, b'\x86', b'')

        class Set(UBXMessage):
            def __init__(self, powerSetupValue=1, period=0, onTime=0):
                payload = struct.pack(
                    '<BBhhBB', 0, powerSetupValue, period, onTime, 0, 0
                )
                UBXMessage.__init__(
                    self, MessageClass.CFG, b'\x86', payload
                )

    class GNSS:

        class Req(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, MessageClass.CFG, b'\x3E', b'')
