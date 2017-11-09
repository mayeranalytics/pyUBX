#ifndef __PARSE_H__
#define __PARSE_H__

#include "parseNMEA.h"
#include "parseNMEABase.h"
#include "parseUBX.h"


class Parse : public ParseUBX , public ParseNMEA, public ParseNMEABase
{
public:
    Parse(char* const buf, const size_t BUFLEN)
    : state(START), ParseUBX(buf, BUFLEN), ParseNMEABase(buf, BUFLEN) {};
    bool parse(uint8_t);

private:
    void onNMEA(char buf[], size_t len) {
        ParseNMEA::parse(ParseNMEABase::buf, ParseNMEABase::BUFLEN);
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
            return ParseNMEABase::parse(c);
        }
        else if(c==0xb5) {
            state = UBX;
            return ParseUBX::parse(c);
        }
        break;
    case NMEA:
        retval = ParseNMEABase::parse(c);
        if(ParseNMEABase::getState() == ParseNMEABase::START)
            state = START;
        return retval;
    case UBX:
        retval = ParseUBX::parse(c);
        if(ParseUBX::getState() == ParseUBX::START)
            state = START;
        return retval;
    default:
        assert(false);  // this shouldn't happen
        return false;
    }
    return false;
}

#endif /* __PARSE_H__ */