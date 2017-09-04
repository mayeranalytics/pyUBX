"""Monitoring Messages: Communication Status, CPU Load, Stack Usage, Task Status. """

from UBXMessage import initMessageClass, addGet
from Types import CH


@initMessageClass
class MON:
    """Message class MON."""

    _class = 0x0A

    @addGet
    class VER:

        _id = 0x04

        class Fields:
            swVersion = CH(1, 30, nullTerminatedString=True)
            hwVersion = CH(2, 10, nullTerminatedString=True)
            class Repeated:
                extension = CH(1, 10, nullTerminatedString=True)
