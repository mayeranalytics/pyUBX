"""Ack/Nak Messages: Acknowledge or Reject messages to CFG input messages."""

from UBXMessage import initMessageClass, addGet
from Types import U1


@initMessageClass
class ACK:
    """Message class ACK."""

    _class = 0x05

    @addGet
    class ACK:

        _id = 0x01

        class Fields:
            clsID = U1(1)
            msgID = U1(2)

    class NAK:

        _id = 0x00

        class Fields:
            clsID = U1(1)
            msgID = U1(2)
