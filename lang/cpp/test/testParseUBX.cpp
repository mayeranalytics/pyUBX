#include <iostream>
#include "../src/messages/MON.h"
#include "../src/parseUBX.h"
#include "../src/serializeUBX.h"
#include "prettyprint.h"
#include "gtest/gtest.h"
#include <string>
#include <cstring>
#include <sstream>

using namespace std;

TEST(Cpp, MON_VER_read) {
    char msg[] = "\x52\x4f\x4d\x20\x43\x4f\x52\x45\x20\x33\x2e\x30\x31\x20\x28\x31\x30\x37\x38\x38\x38\x29\x00\x00\x00\x00\x00\x00\x00\x00\x30\x30\x30\x38\x30\x30\x30\x30\x00\x00\x46\x57\x56\x45\x52\x3d\x53\x50\x47\x20\x33\x2e\x30\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x50\x52\x4f\x54\x56\x45\x52\x3d\x31\x38\x2e\x30\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x47\x50\x53\x3b\x47\x4c\x4f\x3b\x47\x41\x4c\x3b\x42\x44\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x53\x42\x41\x53\x3b\x49\x4d\x45\x53\x3b\x51\x5a\x53\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";

    string result[] = {
        "FWVER=SPG 3.01",
        "PROTVER=18.00",
        "GPS;GLO;GAL;BDS",
        "SBAS;IMES;QZSS"
    };

    ASSERT_EQ(sizeof(MON::VER), 40);

    MON::VER& ver = *((MON::VER*)msg);
    ASSERT_EQ(string(ver.hwVersion), "00080000");
    ASSERT_EQ(string(ver.swVersion), "ROM CORE 3.01 (107888)");
    size_t j = 0;
    for(MON::VER::iterator i=MON::VER::iter(msg, sizeof(msg)-1); !i.end(); i.next()) {
        ASSERT_EQ(result[j++], string(i->extension));
    }
    ASSERT_EQ(j, 4); // all extensions must appear
    ASSERT_EQ(MON::VER::size(0), 40);
    ASSERT_EQ(MON::VER::size(1), 40+30);
    ASSERT_EQ(MON::VER::size(2), 40+30*2);
    ASSERT_EQ(MON::VER::size(4), 40+30*4);
}

TEST(Cpp, MON_VER_write) {
    char result[] = "\x52\x4f\x4d\x20\x43\x4f\x52\x45\x20\x33\x2e\x30\x31\x20\x28\x31\x30\x37\x38\x38\x38\x29\x00\x00\x00\x00\x00\x00\x00\x00\x30\x30\x30\x38\x30\x30\x30\x30\x00\x00\x46\x57\x56\x45\x52\x3d\x53\x50\x47\x20\x33\x2e\x30\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x50\x52\x4f\x54\x56\x45\x52\x3d\x31\x38\x2e\x30\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x47\x50\x53\x3b\x47\x4c\x4f\x3b\x47\x41\x4c\x3b\x42\x44\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x53\x42\x41\x53\x3b\x49\x4d\x45\x53\x3b\x51\x5a\x53\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";

    string hwVersion = "00080000";
    string swVersion = "ROM CORE 3.01 (107888)";
    string input_extensions[] = {
        "FWVER=SPG 3.01",
        "PROTVER=18.00",
        "GPS;GLO;GAL;BDS",
        "SBAS;IMES;QZSS"
    };

    char buf[sizeof(MON::VER)+4*sizeof(MON::VER::Repeated)] = {0};
    MON::VER& ver = *((MON::VER*)buf);
    strcpy(ver.hwVersion, hwVersion.c_str());
    strcpy(ver.swVersion, swVersion.c_str());
    size_t i = 0;
    for(MON::VER::iterator it=MON::VER::iter(buf, 160); i<4; it.next(), i++) {
        strcpy((char*)it, input_extensions[i].c_str());
    }
    for(size_t i=0; i<160; ++i)
        ASSERT_EQ(buf[i], result[i]);
}

/* For testing purposes serialize to stringstream */
class MySerializer : public SerializeUBX
{
public:
    void writeByte(uint8_t byte) {
        ss << byte;
    }
    stringstream ss;
};

TEST(Cpp, SerializeUBX) {
    MySerializer serializer;
    serializer.serialize<ACK::ACK_>(NULL, 0);
    prettyPrint(serializer.ss.str());
    stringstream result;
    result << '\xb5'<<'\x62'<<'\x05'<<'\x01'<<'\x00'<<'\x00'<<'\x06'<<'\x17';
    ASSERT_EQ(result.str(), serializer.ss.str());
}

TEST(Cpp, SerializeGetUBX) {
    MySerializer serializer;
    serializer.serializeGet<MON::VER>();
    prettyPrint(serializer.ss.str());
    stringstream result;
    result << '\xb5'<<'\x62'<<'\x0a'<<'\x04'<<'\x00'<<'\x00'<<'\x0e'<<'\x34';
    ASSERT_EQ(result.str(), serializer.ss.str());
}

/* For testing purposes serialize to stringstream */
class MyParseUBX : public ParseUBX
{
public:
    MyParseUBX(char* const buf, const size_t BUFLEN) 
    : ParseUBX(buf, BUFLEN) { resetFlags(); }
    void resetFlags() {
        ACK_ACK_called = CFG_PMS_called = error = false;
    }
    bool ACK_ACK_called;
    void onACK_ACK_(ACK::ACK_& msg, size_t len) {
        ACK_ACK_called = true;
    }
    bool CFG_PMS_called;
    void onCFG_PMS(CFG::PMS& msg, size_t len) {
        CFG_PMS_called = true;
    }
    bool error;
    void onUBXerr(uint8_t cls, uint8_t id, uint16_t len, Error err) {
        error = true;
        cout << "Error: " << err << endl;
    }

};

TEST(Cpp, ParseUBX) {
    const size_t BUFLEN=256;
    char buf[BUFLEN];
    MyParseUBX deserializer(buf, BUFLEN);
    // test ACK-ACK
    stringstream ack;
    ack << '\xb5'<<'\x62'<<'\x05'<<'\x01'<<'\x00'<<'\x00'<<'\x06'<<'\x17';
    deserializer.resetFlags();
    for(size_t i=0; i<ack.str().size(); i++) {
        deserializer.parse(ack.str().c_str()[i]);
    }
    ASSERT_TRUE(deserializer.ACK_ACK_called && !deserializer.error);
    // test CGF-PMS
    stringstream CFG_PMS_Get;
    CFG_PMS_Get <<  '\xb5'<<'b'<<'\x06'<<'\x86'<<'\x00'<<'\x00'<<'\x8c'<<'\xaa';
    deserializer.resetFlags();
    for(size_t i=0; i<CFG_PMS_Get.str().size(); i++) {
        deserializer.parse(CFG_PMS_Get.str().c_str()[i]);
    }
    ASSERT_TRUE(deserializer.CFG_PMS_called && !deserializer.error);
}

int
main(int argc, char **argv) {
    ::testing::InitGoogleTest( &argc, argv );
    return RUN_ALL_TESTS();
}
