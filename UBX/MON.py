"""Monitoring Messages: Communication Status, CPU Load, Stack Usage, Task Status. """

from UBXMessage import UBXMessage, initMessageClass, stringFromByteString, addGet
from Types import CH


@initMessageClass
class MON:
    """Message class MON."""

    _class = 0x0A

    @addGet
    class VER:

        _id = 0x04

        class Fields:
            swVersion = CH(1, 30)
            hwVersion = CH(2, 10)
            class Repeated:
                extension = CH(1, 10)

        def __init__(self, payload):
            N = (len(payload) - 40)//30
            self.swVersion = stringFromByteString(payload[0:30])
            self.hwVersion = stringFromByteString(payload[30:40])
            self.extension = [
                stringFromByteString(payload[(40+30*i):(40+30*i+30)])
                for i in range(N)
            ]

        def __str__(self):
            s = "MON-VER:"
            s += "\n  swVersion=" + self.hwVersion
            s += "\n  hwVersion=" + self.swVersion
            for ext in self.extension:
                s += "\n  " + ext
            return s
