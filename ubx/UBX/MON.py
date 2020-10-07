"""Monitoring Messages: Communication Status, CPU Load, Stack Usage, Task Status. """

from ubx.UBXMessage import initMessageClass, addGet
from ubx.Types import CH, U, U1, U2, U4, X1, X4

@initMessageClass
class MON:
    """Message class MON."""

    _class = 0x0A

    @addGet
    class VER:

        _id = 0x04

        class Fields:
            swVersion = CH(1, 30, nullTerminatedString=True)
            hwVersion = CH(2, 10, nullTerminatedString=True)
            class Repeated:
                extension = CH(1, 30, nullTerminatedString=True)

    @addGet
    class HW:
        """§31.17.3.1 Hardware Status."""

        _id = 0x09

        class Fields:
            pinSel = X4(1)  # Mask of Pins Set as Peripheral/PIO
            pinBank = X4(2) # Mask of Pins Set as Bank A/B
            pinDir = X4(3)  # Mask of Pins Set as Input/Output
            pinVal = X4(4)  # Mask of Pins Value Low/High
            noisePerMS = U2(5)   # Noise Level as measured by the GPS Core
            agcCnt = U2(6)   # AGC Monitor (counts SIGHI xor SIGLO, range 0 to 8191)
            aStatus = U1(7)  # Status of the Antenna Supervisor State Machine (0=INIT, 1=DONTKNOW, 2=OK, 3=SHORT, 4=OPEN)
            aPower = U1(8)   # Current PowerStatus of Antenna (0=OFF, 1=ON, 2=DONTKNOW)
            flags = X1(9)    # Flags (see graphic below)
            reserved1 = U1(10)
            usedMask = X4(11) # Mask of Pins that are used by the Virtual Pin Manager
            VP = CH(12, 17)   # Array of Pin Mappings for each of the 17 Physical Pins
            jamInd = U1(13)   # CW Jamming indicator, scaled (0 = no CW jamming, 255 = strong CW jamming)
            reserved2 = U2(14)
            pinIrq = X4(15)   # Mask of Pins Value using the PIO Irq
            pullH = X4(16)    # Mask of Pins Value using the PIO Pull High Resistor
            pullL = X4(17)  # Mask of Pins Value using the PIO Pull Low Resistor

    @addGet
    class SPAN:
        """3.14.12.1 Signal Characteristics."""

        _id = 0x31

        class Fields:
            version = U1(1, allowed={0: "SPAN Message V 0"})  # Message version (Currently 0)
            numRfBlocks = U1(2)  # Number of RF blocks included
            reserved0 = U(3,2)  # Reserved
            class Repeated:
                spectrum = U(1,256)  # Spectrum Bins (dB unreferenced)
                span = U4(2)  # Spectrum span (Hz)
                res = U4(3)  # Bin Resolution (Hz)
                center = U4(4)  # Center of spectrum span (Hz)
                pga = U1(5)  # PGA gain (dB)
                reserved1 = U(6,3)  # Reserved

        @property
        def spectra(self):
            return [{
                "centerFreq": self.__getattribute__(f'center_{blockNum}'),
                "span": self.__getattribute__(f'span_{blockNum}'),
                "res": self.__getattribute__(f'res_{blockNum}'),
                "pga": self.__getattribute__(f'pga_{blockNum}'),
                "spectrumBinCenterFreqs": [ self.__getattribute__(f'center_{blockNum}') + self.__getattribute__(f'span_{blockNum}') * (i - 128) / 256 for i in range(256)],
                "spectrum": [rfBin for rfBin in self.__getattribute__(f'spectrum_{blockNum}')]
            } for blockNum in range(1,self.numRfBlocks+1) ]