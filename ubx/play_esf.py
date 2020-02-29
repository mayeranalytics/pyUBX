#!/usr/bin/env python3
"""A space to play around with messages."""

from ubx import UBX
import serial, time, math
from ubx.UBXESFSensor import *


if __name__ == '__main__':
    ser = serial.Serial('COM4', 115200, timeout=None)
    loop_delay_sec = 0.05
    data_id = 2
    for idx in range(100000000):
        timestamp_ms = int(1000 * loop_delay_sec * idx)
        t = timestamp_ms / 1e3
        offset = 2 * math.pi / 3
        v1, v2, v3 = math.sin(t + 0), math.sin(t + offset), math.sin(t + 2*offset),

        measurements = [
            SensorMeasurement(data_id, SensorDataType.GYRO_X, v1),
            SensorMeasurement(data_id, SensorDataType.GYRO_Y, v2),
            SensorMeasurement(data_id, SensorDataType.GYRO_Z, v3),
            SensorMeasurement(data_id, SensorDataType.ACCEL_X, v1),
            SensorMeasurement(data_id, SensorDataType.ACCEL_Y, v2),
            SensorMeasurement(data_id, SensorDataType.ACCEL_Z, v3),
            SensorMeasurement(data_id, SensorDataType.WHEELTICK_FR, int(1000 * v1)),
            SensorMeasurement(data_id, SensorDataType.WHEELTICK_FL, int(1000 * v2)),
            SensorMeasurement(data_id, SensorDataType.WHEELTICK_RR, int(500 * v1)),
            SensorMeasurement(data_id, SensorDataType.WHEELTICK_RL, int(500 * v2)),
            SensorMeasurement(data_id, SensorDataType.WHEELTICK_SINGLE, int(2000 * v3)),
            SensorMeasurement(data_id, SensorDataType.SPEED, v1),
            SensorMeasurement(data_id, SensorDataType.GYRO_TEMPERATURE, v1),
        ]

        esf = UBX.ESF.MEAS.create(timestamp_ms, measurements, id=data_id)
        ser.write(esf.serialize())
        time.sleep(loop_delay_sec)
