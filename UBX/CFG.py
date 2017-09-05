"""Configuration Input Messages: Set Dynamic Model, Set DOP Mask, Set Baud Rate, etc."""

from UBXMessage import UBXMessage, initMessageClass, addGet
import struct
from Types import U1, U2, U4, X4, U


@initMessageClass
class CFG:
    """Message class CFG."""

    _class = 0x06

    @addGet
    class PMS:

        _id = 0x86

        class Fields:
            version = U1(1)
            powerSetupValue = U1(2)
            period = U2(3)
            onTime = U2(4)
            reserved = U2(5)

        class Set(UBXMessage):
            def __init__(self, powerSetupValue=1, period=0, onTime=0):
                payload = struct.pack(
                    '<BBhhBB', 0, powerSetupValue, period, onTime, 0, 0
                )
                UBXMessage.__init__(
                    self, CFG._class, CFG.PMS._id, payload
                )

    @addGet
    class GNSS:

        _id = 0x3E

        class Fields:
            msgVer = U1(1)
            numTrkChHw = U1(2)
            numTrkChUse = U1(3)
            numConfigBlocks = U1(4)
            class Repeated:
                gnssId = U1(1)
                resTrkCh = U1(2)
                maxTrkCh = U1(3)
                reserved = U1(4)
                flags = X4(5)

    @addGet
    class PM2:
        """§31.11.20.2 Extended Power Management configuration."""

        _id = 0x3B

        class Fields:
            version = U1(1)  # Message version (0x02 for this version)
            reserved1 = U1(2)  # Reserved
            maxStartupStartupDur = U1(3)  # Maximum time to spend in Acquisition state. If 0: bound disabled (see maxStartupStateDur). (not supported in protocol versions less than 17), (not supported in protocol versions 23 to 23.01)
            reserved2 = U1(4)  # Reserved
            flags = X4(5)  # PSM configuration flags (see graphic below)
            updatePeriod = U4(6) 	# ms  Position update period. If set to 0, the receiver will never retry a fix and it will wait for external events
            searchPeriod = U4(7) 	# ms  Acquisition retry period if previously failed. If set to 0, the receiver will never retry a startup (not supported in protocol versions 23 to 23.01)
            gridOffset = U4(8) 	# ms  Grid offset relative to GPS start of week (not supported in protocol versions 23 to 23.01)
            onTime = U2(9)  # s  Time to stay in Tracking state (not supported in protocol versions 23 to 23.01)
            minAcqTime = U2(10)  # s  minimal search time
            reserved3 = U(11, 20) 	# Reserved
            extintInactivityMs = U4(12)  # ms  inactivity time out on EXTINT pint if enabled
