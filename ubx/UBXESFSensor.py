from enum import IntEnum
import struct


class SensorDataType(IntEnum):
    NONE = 0
    GYRO_Z = 5  # deg/s *2^-12
    WHEELTICK_FL = 6
    WHEELTICK_FR = 7
    WHEELTICK_RL = 8
    WHEELTICK_RR = 9
    WHEELTICK_SINGLE = 10
    SPEED = 11  # m/s * 1e-3
    GYRO_TEMPERATURE = 12  # deg Celsius * 1e-2
    GYRO_Y = 13  # deg/s *2^-12
    GYRO_X = 14  # deg/s *2^-12
    ACCEL_X = 16  # m/s^2 *2^-10
    ACCEL_Y = 17  # m/s^2 *2^-10
    ACCEL_Z = 18

    @staticmethod
    def values():
        return set(item.value for item in SensorDataType)


class SensorTransform:
    scaler = {
        SensorDataType.WHEELTICK_FL: {
            'forward': lambda x: SensorTransform.convert_tick2wire(x),
            'backward': lambda x: SensorTransform.convert_wire2tick(x)},
        SensorDataType.WHEELTICK_FR: {
            'forward': lambda x: SensorTransform.convert_tick2wire(x),
            'backward': lambda x: SensorTransform.convert_wire2tick(x)},
        SensorDataType.WHEELTICK_RL: {
            'forward': lambda x: SensorTransform.convert_tick2wire(x),
            'backward': lambda x: SensorTransform.convert_wire2tick(x)},
        SensorDataType.WHEELTICK_RR: {
            'forward': lambda x: SensorTransform.convert_tick2wire(x),
            'backward': lambda x: SensorTransform.convert_wire2tick(x)},
        SensorDataType.WHEELTICK_SINGLE: {
            'forward': lambda x: SensorTransform.convert_tick2wire(x),
            'backward': lambda x: SensorTransform.convert_wire2tick(x)},
        SensorDataType.SPEED: {
            'forward': lambda x: SensorTransform.scale_float2int(x, 1e3),
            'backward': lambda x: SensorTransform.scale_int2float(x, 1e3)},
        SensorDataType.GYRO_TEMPERATURE: {
            'forward': lambda x: SensorTransform.scale_float2int(x, 1e2),
            'backward': lambda x: SensorTransform.scale_int2float(x, 1e2)},
        SensorDataType.GYRO_X: {
            'forward': lambda x: SensorTransform.scale_float2int(x, 2 ** 12),
            'backward': lambda x: SensorTransform.scale_int2float(x, 2 ** 12)},
        SensorDataType.GYRO_Y: {
            'forward': lambda x: SensorTransform.scale_float2int(x, 2 ** 12),
            'backward': lambda x: SensorTransform.scale_int2float(x, 2 ** 12)},
        SensorDataType.GYRO_Z: {
            'forward': lambda x: SensorTransform.scale_float2int(x, 2 ** 12),
            'backward': lambda x: SensorTransform.scale_int2float(x, 2 ** 12)},
        SensorDataType.ACCEL_X: {
            'forward': lambda x: SensorTransform.scale_float2int(x, 2 ** 10),
            'backward': lambda x: SensorTransform.scale_int2float(x, 2 ** 10)},
        SensorDataType.ACCEL_Y: {
            'forward': lambda x: SensorTransform.scale_float2int(x, 2 ** 10),
            'backward': lambda x: SensorTransform.scale_int2float(x, 2 ** 10)},
        SensorDataType.ACCEL_Z: {
            'forward': lambda x: SensorTransform.scale_float2int(x, 2 ** 10),
            'backward': lambda x: SensorTransform.scale_int2float(x, 2 ** 10)}
    }

    @staticmethod
    def scale_float2int(x, scaler):
        payload = int(x * scaler).to_bytes(3, byteorder='little', signed=True)
        return int.from_bytes(payload, byteorder='little')

    @staticmethod
    def scale_int2float(x, scaler):
        x = -(x & 0x7fffff) if x & 0x800000 else x
        return float(x) / scaler

    @staticmethod
    def convert_tick2wire(x):
        return ((x < 0) << 23) | abs(x)

    @staticmethod
    def convert_wire2tick(x):
        x = -(x & 0x7fffff) if x & 0x800000 else x
        return x

    @staticmethod
    def transform(data_type, value):
        value = SensorTransform.scaler.get(data_type)['forward'](value)
        if value > 0xffffff:
            raise ValueError('value out of range')
        return value

    @staticmethod
    def inverse_transform(data_type, value):
        return SensorTransform.scaler.get(data_type)['backward'](value)


class SensorMeasurement:

    def __init__(self, data_id: int, data_type: SensorDataType, value):
        self._type = 0
        self._value = 0
        self._id = 0
        self.type = data_type
        self.value = value
        self.id = data_id

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, data_type) -> SensorDataType:
        if data_type not in SensorDataType.values():
            raise ValueError('data_type does not exist')
        self._type = SensorDataType(data_type)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, data_id):
        if data_id > 0x03:
            raise ValueError('data_id out of range')
        self._id = data_id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # test for validity by transforming
        SensorTransform.transform(self.type, self.value)
        self._value = value

    @staticmethod
    def from_integer(payload):
        _id = payload >> 30
        _type = payload >> 24 & 0x1f
        _value = SensorTransform.inverse_transform(_type, payload & 0xffffff)
        return SensorMeasurement(_id, _type, _value)

    def to_bytes(self):
        value_converted = SensorTransform.transform(self.type, self.value)
        return struct.pack('<I', self.id << 30 | self.type << 24 | value_converted)
