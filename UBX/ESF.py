"""Navigation result messages"""

from UBXMessage import initMessageClass, addGet, parseUBXPayload
import struct
import UBXESFSensor
from Types import U2, U4, X2, X4


@initMessageClass
class ESF:
    """Message class ESF."""

    _class = 0x10

    @addGet
    class MEAS:

        _id = 0x02

        class Fields:
            timeTag = U4(1)
            flags = X2(2)
            id = U2(3)

            class Repeated:
                data = X4(1)

            # how are optional fields handled?
            #calibTtag = U4(5)

        @property
        def numMeas(self):
            return self.flags >> 11 & 0x1f

        @property
        def measurements(self):
            datas = (self.__getattribute__(f'data_{idx}') for idx in range(1, self.numMeas+1))
            return [UBXESFSensor.SensorMeasurement.from_integer(d) for d in datas]

        @staticmethod
        def create(timeTag, measurements, timeMarkSent=0, timeMarkEdge=0, calibTtagValid=0, id=0):
            flags = ESF.MEAS._calculate_flags(timeMarkSent, timeMarkEdge, calibTtagValid, numMeas=len(measurements))
            payload = struct.pack('<IHH', timeTag, flags, id) + b''.join(x.to_bytes() for x in measurements)
            return parseUBXPayload(ESF._class, ESF.MEAS._id, payload)

        @staticmethod
        def _calculate_flags(timeMarkSent=0, timeMarkEdge=0, calibTtagValid=0, numMeas=0):
            return ((numMeas & 0x1f) << 11) | \
                   ((calibTtagValid & 0x01) << 3) | \
                   ((timeMarkEdge & 0x01) << 2) | \
                    (timeMarkSent % 0x03)
