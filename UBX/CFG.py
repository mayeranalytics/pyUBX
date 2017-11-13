"""Configuration Input Messages: Set Dynamic Model, Set DOP Mask, Set Baud Rate, etc."""

from UBXMessage import UBXMessage, initMessageClass, addGet
import struct
from Types import U1, U2, U4, X2, X4, U, I2, I4


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
        u"""GNSS system configuration. §31.11.10."""

        _id = 0x3E

        class Fields:
            msgVer = U1(1)
            numTrkChHw = U1(2)
            numTrkChUse = U1(3)
            numConfigBlocks = U1(4)
            class Repeated:
                gnssId = U1(
                    1,
                    allowed={
                        0: 'GPS',
                        1: 'SBAS',
                        2: 'Galileo',
                        3: 'BeiDou',
                        4: 'IMES',
                        5: 'QZSS',
                        6: 'GLONASS',
                    })
                resTrkCh = U1(2)
                maxTrkCh = U1(3)
                reserved = U1(4)
                flags = X4(5)

    @addGet
    class PM2:
        u"""§31.11.20 Extended Power Management configuration."""

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

    @addGet
    class RATE:
        u"""§31.11.24 Navigation/Measurement Rate Settings."""

        _id = 0x08

        class Fields:
            measRate = U2(1)
            navRate = U2(2)
            timeRef = U2(
                3,
                allowed={
                    0: "UTC time",
                    1: "GPS time",
                    2: "GLONASS time",
                    3: "BeiDou time",
                    4: "Galileo time"
                })

    @addGet
    class RXM:
        u"""§31.11.27 RXM configuration.

        For a detailed description see section 'Power Management'.
        """

        _id = 0x11

        class Fields:
            reserved1 = U1(1)   # reserved
            lpMode = U1(        # Low Power Mode
                2,
                allowed={
                    0: "Continuous Mode",
                    1: "Power Save Mode",
                    4: "Continuous Mode"    # for ver>=14 0 and 4 are the same
                    }
            )

    class PRT:
        u"""§31.11.22.4 Port Configuration."""

        _id = 0x00

        class Fields:
            portID      = U1(1)
            reserved1   = U1(2)
            txReady     = X2(3)
            mode        = X4(4)
            reserved2   = U4(5)
            inProtoMask = X2(6)
            outProtoMask= X2(7)
            flags       = X2(8)
            reserved3   = U2(9)

    class PRT_GET:
        u"""§31.11.22.4 Port Configuration."""

        _id = 0x00

        class Fields:
            portID      = U1(1)

    @addGet
    class TP5:
        u"""§31.11.32.3 Time Pulse Parameters."""

        _id = 0x31

        class Fields:
            tpIdx = U1(1)   # Time pulse selection (0 = TIMEPULSE, 1 = TIMEPULSE2)
            version = U1(2)  # Message version (0x00 for this version)
            reserved2 = U2(3)
            antCableDelay = I2(4)  # Antenna cable delay
            rfGroupDelay = I2(5)  # RF group delay
            freqPeriod = U4(6)  # Frequency or period time, depending on setting of bit 'isFreq'
            freqPeriodLock = U4(7)  # Frequency or period time when locked to GPS time, only used if 'lockedOtherSet' is set
            pulseLenRatio = U4(8)  # Pulse length or duty cycle, depending on 'isLength'
            pulseLenRatioLock = U4(9)  # Pulse length or duty cycle when locked to GPS time, only used if 'lockedOtherSet' is set
            userConfigDelay = I4(10)  # User configurable time pulse delay
