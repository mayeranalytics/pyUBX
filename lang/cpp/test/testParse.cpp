#include <iostream>
#include "../src/parse.h"
#include "prettyprint.h"
#include "gtest/gtest.h"
#include <string>
#include <cstring>

using namespace std;

class MyParse : public Parse {
public:
    MyParse(char* const buf, const size_t BUFLEN) : Parse(buf, BUFLEN) {
        resetFlags();
    }
    void resetFlags() {
        onACK_ACK_called = false;
        onGGA_called = false;
    }
    void onACK_ACK_(ACK::ACK_&, size_t len) {
        onACK_ACK_called = true;
    }
    bool onACK_ACK_called;
    void onGGA(
        uint32_t utc, 
        float    lat, 
        float    lon,
        uint8_t  qual,
        uint8_t  n_satellites,
        float    hdil,
        float    alt,
        float    height
    ) {
        onGGA_called = true;
    }
    bool onGGA_called;
};

TEST(Parse, UBX) {
    const size_t BUFLEN=256;
    char buf[BUFLEN];
    MyParse parse(buf, BUFLEN);
    char msg[] = "\xb5\x62\x05\x01\x00\x00\x06\x17"; // ACK-ACK
    for(size_t i=0; i<sizeof(msg)-1; i++) {
        parse.parse(msg[i]);
    }
    ASSERT_TRUE(parse.onACK_ACK_called);
}

TEST(Parse, NMEA) {
    const size_t BUFLEN=256;
    char buf[BUFLEN];
    MyParse parse(buf, BUFLEN);
    char msg[] = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47-0123456";
    for(size_t i=0; i<sizeof(msg)-1; i++)
        parse.parse(msg[i]);
    ASSERT_TRUE(parse.onGGA_called);
}

TEST(Parse, NMEA_too_long) {
    const size_t BUFLEN=2;
    char buf[BUFLEN];
    char msg[] = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47";
    MyParse parse(buf, BUFLEN);
    for(size_t i=0; i<sizeof(msg); i++) {
        parse.parse(msg[i]);
    }
    ASSERT_FALSE(parse.onGGA_called);
}

int
main(int argc, char **argv) {
    ::testing::InitGoogleTest( &argc, argv );
    return RUN_ALL_TESTS();
}
