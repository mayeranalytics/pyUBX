#ifndef __PARSENMEABASE_H__
#define __PARSENMEABASE_H__

#include <stdio.h>
#include <stdint.h>
#include <cassert>


/* Parse NMEA messages.
 *
 * Call parse(uint8_t) on each new byte. On a correct NMEA message the function onNMEA will be 
 * called. On error the function onNMEAError will be called.
 */
class ParseNMEABase
{
public:
    const size_t BUFLEN;
    char* const buf;
    
    /* Constructor. */
    ParseNMEABase(char* const buf, const size_t BUFLEN)
     : BUFLEN(BUFLEN), buf(buf), state(START), buf_pos(0) {};
    
    /* Parse one new byte. */
    bool parse(uint8_t);

    /* NMEA callback. You must implement this in a derived class.
     *
     * buf is guaranteed to be a null-terminated string.
     */
     virtual void onNMEA(char buf[], size_t len) = 0;
    
     /* NMEA error callback
     *
     * Override this function if needed.
     */
    virtual void onNMEAerr() {};
        
    virtual ~ParseNMEABase() {};

    enum STATE {START, NMEA, NMEA_CKSUM_1, NMEA_CKSUM_2};

    /* Return state */
    STATE getState() const { return state; }
        
private:
    ParseNMEABase();
    STATE state;
    size_t buf_pos;     // current position in buf
    // NMEA state variables and functions
    uint8_t NMEA_cksum_calculated, NMEA_cksum_in_message;
protected:
    /* Convert a single hex char (0-9, A-F) to a number (0-15), 0xff indicates an error.
    */
    uint8_t hexToInt(char c);
};


bool
ParseNMEABase::parse(uint8_t c)
{
    if(buf_pos >= BUFLEN) {
        #ifdef DEBUG
        printf("ParseNMEABase::BUFLEN exceeded while parsing NMEA message\n");
        #endif
        state = START;
        onNMEAerr();
        return false;
    } 
    
    uint8_t i;
    switch(state) {
    case START:
        if(c == '$') {
            state = NMEA;
            buf_pos = 0;
            NMEA_cksum_calculated = 0;
        }
        break;
    case NMEA:
        if(c == '*')
            state = NMEA_CKSUM_1;
        else {
            //printf("-%ld\n", buf_pos);
            buf[buf_pos++] = c;
            NMEA_cksum_calculated ^= c; // update cksum
        }
        break;
    case NMEA_CKSUM_1:
        i = hexToInt(c);
        if(i == 0xff) {
            state = START;
            #ifdef DEBUG
            printf("%c in NMEA cksum is not hex\n", c);
            #endif
        } else {
            NMEA_cksum_in_message = 16 * i;
            state = NMEA_CKSUM_2;
        }
        break;
    case NMEA_CKSUM_2:
        i = hexToInt(c);
        if(i != 0xff) {
            NMEA_cksum_in_message += hexToInt(c);
            if(NMEA_cksum_calculated == NMEA_cksum_in_message) {
                buf[buf_pos] = 0;   // make a null terminated string
                onNMEA(buf, buf_pos);
            } else {
                #ifdef DEBUG
                printf("NMEA cksum mismatch: is 0x%02X, should be 0x%02X\n", NMEA_cksum_calculated, NMEA_cksum_in_message);
                #endif
                buf[buf_pos] = 0;   // make a null terminated string
                onNMEAerr();
            }
        } else {
            #ifdef DEBUG
            printf("%c in NMEA cksum is not hex\n", c);
            #endif
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
ParseNMEABase::hexToInt(char c)
{
    if(c >= '0' && c <= '9')
        return c - '0';
    else if(c >= 'A' && c <= 'F')
        return c - 'A' + 10;
    else
        return 0xff;
}

#endif /* __PARSENMEABASE_H__ */
