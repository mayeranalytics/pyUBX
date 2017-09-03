"""Ack/Nak Messages: Acknowledge or Reject messages to CFG input messages."""

from UBXMessage import initMessageClass
from Types import U1
import struct


@initMessageClass
class ACK:
    """Message class ACK."""

    _class = 0x05

    class ACK:

        _id = 0x01

        class Fields:
            clsID = U1()
            msgID = U1()

    class NAK:

        _id = 0x00

        class Fields:
            clsID = U1()
            msgID = U1()
