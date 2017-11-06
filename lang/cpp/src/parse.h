#ifndef __PARSE_H__
#define __PARSE_H__

#include "parseNMEA.h"
#include "parseNMEAPayload.h"
#include "parseUBX.h"


class Parse : public ParseUBX , public ParseNMEA, public ParseNMEAPayload
{
public:
    Parse(char* const buf, const size_t BUFLEN)
    : state(START), ParseUBX(buf, BUFLEN), ParseNMEA(buf, BUFLEN) {};
    bool parse(uint8_t);

private:
    void onNMEA(char buf[], size_t len) {
        ParseNMEAPayload::parse(ParseNMEA::buf, ParseNMEA::BUFLEN);
    }
    enum STATE { START, UBX, NMEA } state;
    Parse();
};


bool
Parse::parse(uint8_t c) {
    bool retval;
    switch(state) {
    case START:
        if(c == '$') { 
            state = NMEA;
            return ParseNMEA::parse(c);
        }
        else if(c==0xb5) {
            state = UBX;
            return ParseUBX::parse(c);
        }
        break;
    case NMEA:
        retval = ParseNMEA::parse(c);
        if(ParseNMEA::getState() == ParseNMEA::START)
            state = START;
        return retval;
        break;
    case UBX:
        retval = ParseUBX::parse(c);
        if(ParseUBX::getState() == ParseUBX::START)
            state = START;
        return retval;
    break;
    default:
        assert(false);  // this shouldn't happen
        return false;
    }
    return false;
}

#endif /* __PARSE_H__ */