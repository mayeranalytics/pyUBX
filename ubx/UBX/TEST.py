"""Solely for testing purposes. """

from ubx.UBXMessage import initMessageClass, addGet
from ubx.Types import U1, U2


@initMessageClass
class TEST:
    """Message class TEST."""

    _class = 0xFF

    @addGet
    class TEST:
        """to test"""

        _id = 0xFF

        class Fields:
            first = U1(1)
            second = U1(2)
            class Repeated:
                ext = U2(1)
