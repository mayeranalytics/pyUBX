"""TODO."""
from enum import Enum
import UBX


def isObj(obj, cls):
    """Test if UBX message obj is of class cls."""
    return obj._class == cls._class and obj._id == cls._id


def isACK(obj):
    """Test whether message obj is a ACK."""
    return isObj(obj, UBX.ACK.ACK)


def isNAK(obj):
    """Test whether message obj is a NAK."""
    return isObj(obj, UBX.ACK.NAK)


def FSM_Get(msgCls):
    """Decorator that makes a getter FSM for use in Manager."""
    def decorator(FSMCls):
        # 1. class STATE
        class STATE(Enum):
            START = 0
            DONE = 1
        setattr(FSMCls, "STATE", STATE)
        # 2. function __init__
        def __init__(self):
            self.state = FSMCls.STATE.START
            self.ver = None
        setattr(FSMCls, "__init__", __init__)
        # 3. function done
        def done(self):
            return self.state == FSMCls.STATE.DONE
        setattr(FSMCls, "done", done)
        # 4. function onUBX
        def onUBX(self, obj, manager):
            if obj._class == msgCls._class and obj._id == msgCls._id:
                print(obj)
                self.state = FSMCls.STATE.DONE
        setattr(FSMCls, "onUBX", onUBX)
        return FSMCls
    return decorator
