#ifndef __PARSEUBX_H__
#define __PARSEUBX_H__

#include <stdio.h>
#include <stdint.h>
#include <cassert>

/* Parse UBX messages.
 *
 * Feed in newly read bytes with parse(uint8_t). On correct parse the function
 * onUBX is called. On error the function onUBXerr is called. You must
 * derive from this class and implement onUBX. If you want error callbacks you
 * must override onUBXerr, too.
 */
class ParseUBX
{
public:
    static const size_t BUFLEN = 256;
    char buf[BUFLEN];

    /* Constructor.
     */
    ParseUBX() : state(START) {};
    bool parse(uint8_t);

    /* NMEA callback
     *
     * buf is guaranteed to be a null-terminated string.
     */
    virtual void onUBX(uint8_t cls, uint8_t id, size_t len, char buf[]) = 0;

    enum Error {BuflenExceeded, BadChksum, NotImplemented, Other};

    /* UBX error callback
     *
     * Override this function.
     */
    virtual void onUBXerr(uint8_t cls, uint8_t id, uint16_t len, Error err) {};

    virtual ~ParseUBX() {};

private:
    enum STATE {START, UBX_SYNC_CHAR_2, UBX_CLASS, UBX_ID, UBX_LEN_1, UBX_LEN_2,
                UBX_PAYLOAD, UBX_CK_A, UBX_CK_B};
    STATE state;
    size_t buf_pos;     // current position in buf
    // UBX state variables and functions
    uint8_t UBX_ck_a_calculated, UBX_ck_b_calculated;
    uint8_t UBX_ck_a_in_message;
    uint16_t UBX_payload_len;
    uint16_t UBX_payload_len_counter;
    uint8_t UBX_class;
    uint8_t UBX_id;
    void UBX_update_ck(char c);

protected:
    /* Convert a single hex char (0-9, A-F) to a number (0-15), 0xff indicates an error.
     */
    uint8_t hexToInt(char);
};

bool
ParseUBX::parse(uint8_t c)
{
    uint8_t i;
    switch(state) {
    case START:
        if(c == 0xb5)
            state = UBX_SYNC_CHAR_2;
        break;
    case UBX_SYNC_CHAR_2:
        if(c == 0x62) {
            UBX_ck_a_calculated = UBX_ck_b_calculated = 0;
            state = UBX_CLASS;
        } else
            state = START;
        break;
    case UBX_CLASS:
        UBX_class = c;
        UBX_update_ck(c);
        state = UBX_ID;
        break;
    case UBX_ID:
        UBX_id = c;
        UBX_update_ck(c);
        state = UBX_LEN_1;
        break;
    case UBX_LEN_1:
        UBX_payload_len = uint16_t(c);  // little endian
        UBX_update_ck(c);
        state = UBX_LEN_2;
        break;
    case UBX_LEN_2:
        UBX_payload_len |= uint16_t(c) << 8;
        UBX_update_ck(c);
        if(UBX_payload_len==0)
            state = UBX_CK_A;
        else if(UBX_payload_len > BUFLEN) {
            #ifdef DEBUG
            printf("ParseUBX::BUFLEN exceeded while parsing UBX message\n");
            #endif
            onUBXerr(UBX_class, UBX_id, BUFLEN, BuflenExceeded);
            state = START;
            return false;
        } else {
            UBX_payload_len_counter = UBX_payload_len;
            buf_pos = 0;
            state = UBX_PAYLOAD;
        }
        break;
    case UBX_PAYLOAD:   // only entered here when UBX_payload_len_counter > 0
        --UBX_payload_len_counter;
        buf[buf_pos++] = c;
        UBX_update_ck(c);
        if(UBX_payload_len_counter == 0)
            state = UBX_CK_A;
        break;
    case UBX_CK_A:
        UBX_ck_a_in_message = c;
        state = UBX_CK_B;
        break;
    case UBX_CK_B:
        if(UBX_ck_a_calculated == UBX_ck_a_in_message && UBX_ck_b_calculated == c) {
            onUBX(UBX_class, UBX_id, UBX_payload_len, buf);
        } else {
            #ifdef DEBUG
            printf("UBX cksum mismatch: is 0x%02X%02X, should be 0x%02X%02X\n",
                   UBX_ck_a_calculated, UBX_ck_b_calculated, UBX_ck_a_in_message, c);
            #endif
            onUBXerr(UBX_class, UBX_id, UBX_payload_len, BadChksum);
        }
        state = START;
        break;

    /************************ default shouldn't be reached  *******************/
    default:
        assert(false);
        break;
    }
    return true;
}

uint8_t
ParseUBX::hexToInt(char c)
{
    if(c >= '0' && c <= '9')
        return c - '0';
    else if(c >= 'A' && c <= 'F')
        return c - 'A' + 10;
    else
        return 0xff;
}

void
ParseUBX::UBX_update_ck(char c)
{
    UBX_ck_a_calculated += c;
    UBX_ck_b_calculated += UBX_ck_a_calculated;
}

#endif /* #ifndef __PARSEUBX_H__ */
