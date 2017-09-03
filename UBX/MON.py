"""Monitoring Messages: Communication Status, CPU Load, Stack Usage, Task Status. """

from UBXMessage import UBXMessage, initMessageClass, stringFromByteString
import struct


@initMessageClass
class MON:
    """Message class MON."""

    _class = 0x0A

    class VER:

        _id = 0x04

        def __init__(self, payload):
            N = (len(payload) - 40)//30
            self.swVersion = payload[0:30]
            self.hwVersion = payload[30:40]
            self.extension = [
                payload[(40+30*i):(40+30*i+30)] for i in range(N)
            ]

        def __str__(self):
            s = "swVersion={}\nhwVersion={}".format(
                stringFromByteString(self.hwVersion),
                stringFromByteString(self.swVersion)
            )
            for ext in self.extension:
                s += "\n{}".format(stringFromByteString(ext))
            return s

        class Get(UBXMessage):
            def __init__(self):
                UBXMessage.__init__(self, MON._class, MON.VER._id, b'')
