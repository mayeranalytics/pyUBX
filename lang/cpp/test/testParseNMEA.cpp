#include <gtest/gtest.h>
#include "../src/parseNMEA.h"
#include <string>
#include <cmath>

using namespace std;

class MyParser : public ParseNMEA
{
public:
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
        GGAgood = true;
    }
    bool GGAgood = false;
    void resetFlags() {
        GGAgood = false;
    }
};

TEST(ParseNMEA, parseLatLon)
{
    struct ParseLatLonInput {
        ParseLatLonInput(string ParseLatLoninput, string nsew, float lat_lon) 
        : ParseLatLoninput(ParseLatLoninput), nsew(nsew), lat_lon(lat_lon) {};
        string ParseLatLoninput;
        string nsew;
        float lat_lon;
    };
    
    ParseLatLonInput* parseLatLoninputs[] = {
        new ParseLatLonInput("12300.00", "N", 123.0f),
        new ParseLatLonInput("12330.00", "N", 123.5f),
        new ParseLatLonInput("12300.00", "S", -123.0f),
        new ParseLatLonInput("2300.00", "S", -23.0f),
        new ParseLatLonInput("2330.00", "S", -23.5f),
        new ParseLatLonInput("1230.50", "S", -(12.0f + 30.5f/60.0f)),
        new ParseLatLonInput("01230.50", "S", -(12.0f + 30.5f/60.0f)),
        new ParseLatLonInput("1200.00", "E", 12.0f),
        new ParseLatLonInput("1200.00", "W", -12.0f),
        new ParseLatLonInput("1230.50", "E", 12.0f + 30.5f/60.0f),
        new ParseLatLonInput("10.50", "E", 9999.0f),
        new ParseLatLonInput("100000.50", "E", 9999.0f),
        0
    };
    ParseLatLonInput* parseLatLoninput;
    for(size_t i=0; (parseLatLoninput = parseLatLoninputs[i]) != 0; i++)
    {
        float lat_lon = parseLatLon(parseLatLoninput->ParseLatLoninput.c_str(), parseLatLoninput->nsew.c_str());
        ASSERT_EQ(lat_lon, parseLatLoninput->lat_lon);
    }
}

TEST(ParseNMEA, testParseUTC)
{
    char input1[] = "120000.00";
    ASSERT_EQ(parseUTC(input1), 4320000);
    char input2[] = "120000.01";
    ASSERT_EQ(parseUTC(input2), 4320000+1);
    char input3[] = "010203.04";
    ASSERT_EQ(parseUTC(input3), 372304);
}

TEST(ParseNMEA, testGGA_shallow)
{
    char ParseLatLoninput1[] = "GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,";
    char ParseLatLoninput2[] = "GPGGA,172814.0,3723.46587704,N,12202.26957864,W,2,6,1.2,18.893,M,-25.669,M,2.0,0031";
    char ParseLatLoninput3[] = "GPGGA,181908.00,3404.7041778,N,07044.3966270,W,4,13,1.00,495.144,M,29.200,M,0.10,0000";
    char ParseLatLoninput4[] = "GPGGA,115739.00,4158.8441367,N,09147.4416929,W,4,13,0.9,255.747,M,-32.00,M,01,0000";
    char ParseLatLoninput5[] = "GNGGA,,,,,,0,00,99.99,,,,,,";
    char ParseLatLoninput6[] = "GNGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,";
    char ParseLatLoninput7[] = "GPGGA,092725.00,4717.11399,N,00833.91590,E,1,08,1.01,499.6,M,48.0,M,,";
    char* ParseLatLoninputs[] = {ParseLatLoninput1, ParseLatLoninput2, ParseLatLoninput3, ParseLatLoninput4, 
                                ParseLatLoninput5, ParseLatLoninput6, ParseLatLoninput7, 0};
    MyParser parser;
    for(size_t ParseLatLoninput_count=0; 
        ParseLatLoninputs[ParseLatLoninput_count] != 0; 
        ParseLatLoninput_count++) 
    {
        parser.resetFlags();
        char* ParseLatLoninput = ParseLatLoninputs[ParseLatLoninput_count];
        parser.parse(ParseLatLoninput, strlen(ParseLatLoninput));
        ASSERT_TRUE(parser.GGAgood);
    }
}

TEST(ParseNMEA, testGGA_full_1)
{
    class MyParser : public ParseNMEA
    {
    public:
        void onGGA(uint32_t utc, float lat, float lon, uint8_t qual, uint8_t n_satellites, float hdil, float alt, float height)
        {
            GGAcalled = true;
            ASSERT_EQ(utc, 3404500);
            ASSERT_TRUE(fabsf(47.f + 17.11399f/60.f - lat) < 1e-6f);
            ASSERT_TRUE(fabs(8.f + 33.91590/60.f - lon) < 1e-6f);
            ASSERT_EQ(qual, 1);
            ASSERT_EQ(n_satellites, 8);
            ASSERT_TRUE(fabsf(hdil - 1.01f) < 1e-6f);
            ASSERT_TRUE(fabsf(alt - 499.6f) < 1e-5f);
            ASSERT_TRUE(fabsf(height- 48.0f) < 1e-5f);
        }
        bool GGAcalled = false;
    };
    MyParser parser;
    char input[] = "GPGGA,092725.00,4717.11399,N,00833.91590,E,1,08,1.01,499.6,M,48.0,M,,";
    parser.parse(input, strlen(input));
    ASSERT_TRUE(parser.GGAcalled);
}  

TEST(ParseNMEA, testGGA_full_2)
{
    class MyParser : public ParseNMEA
    {
    public:
        void onGGA(uint32_t utc, float lat, float lon, uint8_t qual, uint8_t n_satellites, float hdil, float alt, float height)
        {
            GGAcalled = true;
            ASSERT_EQ(utc, 2056200);
            ASSERT_EQ(lat, 9999.f);
            ASSERT_EQ(lon, 9999.f);
            ASSERT_EQ(qual, 0);
            ASSERT_EQ(n_satellites, 0);
            ASSERT_TRUE(fabsf(hdil - 99.99f) < 1e-6f);
            ASSERT_TRUE(fabsf(alt - 0.f) < 1e-5f);
            ASSERT_TRUE(fabsf(height- 0.f) < 1e-5f);
        }
        bool GGAcalled = false;
    };
    MyParser parser;
    char input[] = "GNGGA,054242.00,,,,,0,00,99.99,,,,,,";
    parser.parse(input, strlen(input));
    ASSERT_TRUE(parser.GGAcalled);
}  


int main(int argc, char **argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
