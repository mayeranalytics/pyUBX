"""Ack/Nak Messages: Acknowledge or Reject messages to CFG input messages."""

from UBXMessage import UBXMessage, initMessageClass
import struct


@initMessageClass
class ACK:
    """Message class ACK."""

    _class = 0x05

    class ACK:

        _id = 0x01
        _len = 2

        def __init__(self, msg):
            self.clsID, self.msgID = struct.unpack('BB', msg)

        def __str__(self):
            return "ACK-ACK {:02X}:{:02X}".format(self.clsID, self.msgID)

    class NAK:

        _id = 0x00
        _len = 2

        def __init__(self, msg):
            self.clsID, self.msgID = struct.unpack('BB', msg)

        def __str__(self):
            return "ACK-NAK {:02X}:{:02X}".format(self.clsID, self.msgID)
