"""Navigation result messages"""

import math
import datetime
from ubx.UBXMessage import initMessageClass, addGet
from ubx.Types import U1, U2, U4, X1, X2, X4, I1, I2, I4

# Reference for u-blox 9:
# https://www.u-blox.com/sites/default/files/u-blox_ZED-F9P_InterfaceDescription_%28UBX-18010854%29.pdf
# Reference for u-blox 8, which is incompatible with u-blox 9 (especially for RELPOSNED)
# https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_(UBX-13003221)_Public.pdf

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

    @addGet
    class PVT:

        _id = 0x07

        class Fields:
            iTOW = U4(1)
            year = U2(2)
            month = U1(3)
            day = U1(4)
            hour = U1(5)
            min = U1(6)
            sec = U1(7)
            valid = X1(8)
            tAcc = U4(9)
            nano = I4(10)
            fixType = U1(11)
            flags = X1(12)
            flags2 = X1(13)
            numSV = U1(14)
            lon = I4(15)    # 1e-7 deg for lon,lat
            lat = I4(16)
            height = I4(17) # mm for heights; height is above ellipsoid
            hMSL = I4(18)
            hAcc = U4(19)
            vAcc = U4(20)
            velN = I4(21)   # mm/s for speeds and velocities
            velE = I4(22)
            velD = I4(23)
            gSpeed = I4(24)
            headMot = I4(25)    # 1e-5 deg for heading of motion
            sAcc = U4(26)
            headAcc = U4(27)
            pDOP = U2(28)
            flags3 = X1(29)
            reserved1 = U1(30)
            reserved1x = U4(31)
            headVeh = I4(32)
            magDec = I2(33)     # 1e-2 deg for Magnetic declination
            magAcc = U2(34)

        @property
        def UTC(self):
            """
            UTC as a datetime with timezone
            :return:
            """
            return datetime.datetime(year=self.year, month=self.month,
                                     day=self.day, hour=self.hour,
                                     minute=self.min, second=self.sec,
                                     tzinfo=datetime.timezone.utc
                                     ) + datetime.timedelta(seconds=self.nano*1e-9)

        @property
        def position_dm(self):
            """
            geographic position in degrees and meters above MSL

            longitude East, latitude North, Height in meters

            :return: [lon, lat, height_msl]
            """
            return [self.lon * 1e-7, self.lat * 1e-7, self.hMSL * 1e-3]

        @property
        def position_dm_e(self):
            """
            geographic position in degrees and meters above ellipsoid

            longitude East, latitude North, Height in meters

            :return: [lon, lat, height_ellispoid]
            """
            return [self.lon * 1e-7, self.lat * 1e-7, self.height * 1e-3]

        @property
        def velNED_m(self):
            """
            Velocity [North, East, Down] in m/s

            :return: [vN, vE, vD]
            """
            return [self.velN * 1e-3, self.velE * 1e-3, self.velD * 1e-3]

        @property
        def speed_m(self):
            """
            Ground speed in m/s
            :return: speed
            """
            return 1e-3 * self.gSpeed

        def summary(self):
            return ("UBX.NAV.PVT:       {}z  {:12.7f} E {:11.7f} N {:8.1f} m(MSL)"
                .format(self.UTC.isoformat()[:21], *self.position_dm)
                    + " speed = {:.3f} m/s at NED: {:.3f}, {:.3f}, {:.3f}"
                    .format(self.speed_m, *self.velNED_m))

    @addGet
    class RELPOSNED:
        # WARNING: This is for Protocol version 27.11 (uBlox-9)
        #
        _id = 0x3c

        class Fields:
            version = U1(0)
            reserved1 = U1(1)
            refStationID = U2(2)
            iTOW = U4(3)
            relPosN = I4(4)     # WARNING: these cm values must be combined with relPosHP* to get full precision
            relPosE = I4(5)
            relPosD = I4(6)
            relPosLength = I4(7)
            relPosHeading = I4(8)   # 1e-5 Deg
            reserved2 = U4(9)
            relPosHPN = I1(10)   # 0.1 mm resolutionto add to the cm values
            relPosHPE = I1(11)
            relPosHPD = I1(12)
            relPosHPLength = I1(13)
            accN = U4(14)
            accE = U4(15)
            accD = U4(16)
            accLength = U4(17)
            accHeading = U4(18)
            reserved3 = U4(19)
            flags = X4(20)  # bits[0..7] = [gnssFixOK, diffSoln, relPosValid, carrSoln0,arrSoln1, isMoving, refPosMiss, refObsMiss]

        @property
        def relPosNED_m(self):
            """
            Relative Position in meters
            :return: [North_m,East_m,Down_m]
            """
            return [self.relPosN * 1e-2 + self.relPosHPN * 1e-4,
                    self.relPosE * 1e-2 + self.relPosHPE * 1e-4,
                    self.relPosD * 1e-2 + self.relPosHPD * 1e-4]

        @property
        def heading_deg(self):
            """
            Relative Position Heading in degrees
            :return:
            """
            return self.relPosHeading * 1e-5

        @property
        def length_m(self):
            return self.relPosLength * 1e-2 + self.relPosHPLength * 1e-4

        @property
        def pitch_deg(self):
            """
            Relative Position pitch in degrees
            :return:
            """
            return math.degrees(math.asin(-(self.relPosD * 1e-2 + self.relPosHPD * 1e-4)
                                          / self.length_m))

        @property
        def TOW_str(self):
            mins, millis = divmod(self.iTOW, 60000)
            hours, mins = divmod(mins, 60)
            days, hours = divmod(hours, 24)
            return "{:1d}-{:02d}:{:02d}:{:04.1f}gps".format(days, hours, mins, millis/1000)

        def summary(self):
            return ("UBX.NAV.RELPOSNED: TOW = {} NED = {:8.5f}, {:8.5f}, {:8.5f} m"
                    .format(self.TOW_str, *self.relPosNED_m)
                    + "-> heading {:9.2f} deg, {:8.2f} up, len {:.3f} m"
                    .format(self.heading_deg, self.pitch_deg, self.length_m))
