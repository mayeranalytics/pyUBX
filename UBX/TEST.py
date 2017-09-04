"""Monitoring Messages: Communication Status, CPU Load, Stack Usage, Task Status. """

from UBXMessage import UBXMessage, initMessageClass, stringFromByteString, addGet
from Types import U1, U2


@initMessageClass
class TEST:
    """Message class TEST."""

    _class = 0xFF

    @addGet
    class TEST:

        _id = 0xFF

        class Fields:
            first = U1(1)
            second = U1(2)
            class Repeated:
                ext = U2(1)
