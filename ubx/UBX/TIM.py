"""Timing messages"""

from ubx.UBXMessage import initMessageClass, addGet
from ubx.Types import U1, U2, U4, I4


@initMessageClass
class TIM:
    """Message class TIM."""

    _class = 0x0d

    @addGet
    class SVIN:

        _id = 0x04

        class Fields:
            dur = U4(1)
            meanX = I4(2)
            meanY = I4(3)
            meanZ = I4(4)
            meanV = U4(5)
            obs = U4(6)
            valid = U1(7)
            active = U1(8)
            reserved = U2(9)


