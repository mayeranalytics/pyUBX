"""Monitoring Messages: Communication Status, CPU Load, Stack Usage, Task Status. """

from UBXMessage import UBXMessage, initMessageClass
import struct


@initMessageClass
class MON:
    """Message class MON."""

    _class = 0x0A

    class VER:

        _id = 0x04

        class Req(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, MON._class, MON.VER._id, b'')

        class Res(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, MON._class, MON.VER._id, b'')
