from UBXMessage import UBXMessage, MessageClass
import struct


class MON:
    """Message class MON."""

    class VER:

        class Req(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, MessageClass.MON, b'\x04', b'')

        class Res(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, MessageClass.MON, b'\x04', b'')
