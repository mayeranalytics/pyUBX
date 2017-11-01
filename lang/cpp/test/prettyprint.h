#include <iostream>
#include <string>
#include <cstdio>
#include <cstddef>
#include <sstream>
#include <iomanip>

using namespace std;

/* Pretty print a string (that may contain binary) */
void prettyPrint(const string& s, ostream& os=cout)
{
    size_t len = s.length();
    const char* c_str = s.c_str();
    stringstream hex, ascii;
    char buf[5];
    uint32_t i;
    for(i=0; i<len; i++) {
        if(i % 8 == 0 && i != 0) {
            sprintf(buf, "%04X", uint32_t(i-8));
            os << buf << ": " << hex.str() << "  " << ascii.str() << endl;
            hex.str(""); ascii.str("");
        }
        sprintf(buf, "%02X", uint8_t(c_str[i]));
        hex << buf << " ";
        char c = (c_str[i] >= ' ' && c_str[i]<='~') ? c_str[i] : '.';
        ascii << c;
    }
    if(i<8) i = 8;
    sprintf(buf, "%04X", uint32_t(i-8));
    os << buf << ": " << hex.str() << "  " << ascii.str() << endl;
}
