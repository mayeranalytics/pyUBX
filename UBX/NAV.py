"""Navigation result messages"""

from UBXMessage import UBXMessage, initMessageClass, addGet
import struct
from Types import U1, U2, U4, X1, X2, X4, U, I1, I2, I4


@initMessageClass
class NAV:
    """Message class NAV."""

    _class = 0x01

    @addGet
    class DOP:

        _id = 0x04

        class Fields:
            iTOW = U4(1)
            gDOP = U2(2)
            pDOP = U2(3)
            tDOP = U2(4)
            vDOP = U2(5)
            hDOP = U2(6)
            nDOP = U2(7)
            eDOP = U2(8)

    @addGet
    class SVINFO:

        _id = 0x30

        class Fields:
            iTOW = U4(1)
            numCh = U1(2)
            globalFlags = X1(3,
                                 allowed = {
                                     0 : 'Antaris',
                                     1 : 'u-Blox 5',
                                     2 : 'u-Blox 6',
                                     3 : 'u-Blox 7',
                                     4 : 'u-Blox 8',
                                     })
            reserved1 = U2(4)

            class Repeated:
                chn = U1(1)
                svid = U1(2)
                flags = X1(3)
                quality = X1(4)
                cno = U1(5)
                elev = I1(6)
                axim = I2(7)
                prRes = I4(8)

