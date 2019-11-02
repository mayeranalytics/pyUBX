"""Timing messages"""

from UBXMessage import UBXMessage, initMessageClass, addGet
import struct
from Types import U1, U2, U4, X1, X2, X4, U, I1, I2, I4


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


