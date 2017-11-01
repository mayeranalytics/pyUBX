// define the _iterator

#include <stddef.h>

#ifndef __SERIALIZER_H__
#define __SERIALIZER_H__

class Serializer
{
public:
    virtual void writeByte(uint8_t byte) = 0;
    template<class T>
    void serialize(uint8_t* data, uint16_t len) {
        _serialize(data, len, T::classID, T::messageID);
    }
private:
    struct CkSum {
    public:
        CkSum() : ck_A(0), ck_B(0) {}
        void update(uint8_t byte) {
            ck_A += byte;
            ck_B += ck_A;
        }
        bool match(uint8_t _ck_A, uint8_t _ck_B) const {
            return ck_A == _ck_A && ck_B == _ck_B;
        }
        uint8_t ck_A, ck_B;
    };
    void _serialize(uint8_t* data, uint16_t len, uint8_t classID, uint8_t messageID)
    {
        CkSum ckSum;
        writeByte(0xB5);
        writeByte(0x62);
        writeByte(classID);   ckSum.update(classID);
        writeByte(messageID); ckSum.update(messageID);
        writeByte(len & 0x00ff); ckSum.update(len & 0x00ff);
        writeByte(len >> 8); ckSum.update(len >> 8);
        for(uint16_t i=0; i<len; i++) {
            writeByte(data[i]); ckSum.update(data[i]);
        }
        writeByte(ckSum.ck_A);
        writeByte(ckSum.ck_B);
    }
};

#endif // #define __SERIALIZER_H__
