#ifndef __SERIALIZEUBX_H__
#define __SERIALIZEUBX_H__

#include <stddef.h>

class SerializeUBX
{
public:
    virtual void writeByte(uint8_t byte) = 0;
    /* Serialize message T
     */
    template<class T>
    void serialize(uint8_t* data, uint16_t len) {
        _serialize(data, len, T::classID, T::messageID);
    }
    /* Serialize message T with zero length payload
     */
    template<class T>
    void serialize() {
        _serialize(NULL, 0, T::classID, T::messageID);
    }
    /* Serialize Get message (zero length payload message) corresponding to message T
     */
    template<class T>
    void serializeGet() { serialize<T>(); }
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
    /* Serialize payload at data, length len, with classID and messageID.
     */
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

template<class T>
size_t makeGet(char* buf, const size_t BUFLEN) {

}

#endif // #define __SERIALIZEUBX_H__
