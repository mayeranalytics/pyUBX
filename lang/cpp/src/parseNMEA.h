/*
 * parseNMEA.h
 *
 *  Created on: 26 Oct 2017
 *      Author: mmayer
 */

#ifndef __PARSENMEA_H__
#define __PARSENMEA_H__

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "parseNMEABase.h"


/* Parse NMEA payloads.
 *
 * Call parse(char[] msg, size_t len) on each new NMEA payload. 
 * On a correct NMEA message the respective functions onGGA, etc., will be called. 
 * On error the function onError will be called.
 */
class ParseNMEA
{
public:
    void parse(char buf[], size_t len);

    /* GGA callback 
     */
    virtual void onGGA(
        uint32_t utc, 
        float    lat, 
        float    lon,
        uint8_t  qual,
        uint8_t  n_satellites,
        float    hdil,
        float    alt,
        float    height
    ) {};
    virtual void onError(char buf[], size_t len) {};
};

/* Parse a lat/lon string as given in NMEA messages.
 *
 * Returns a float. 9999 identifies an error.
 */
float parseLatLon(const char s[], const char nsew[]);

/* Parse a UTC timestamp hhmmss.ss 
 */
uint32_t parseUTC(char s[]);

float
parseLatLon(const char _s[], const char nsew[])
{
    // returns 9999 on error
    if(_s[0] == '\0' or nsew[0] == '\0')
        return 9999;
    char* s = const_cast<char*>(_s);    // it is actually const (strings are modified then repaired)
    float lat_lon;
    size_t i;
    for(i=0; ; i++) {
        if(s[i]==0) break;
        if(s[i]=='.') {
            if(i==4) { // format xxmm
                char bkup = s[2];
                s[2] = 0;
                lat_lon=float(atoi(s));
                s[2] = bkup;
                lat_lon += strtod(s+2, NULL) / 60.0f;
            } else if(i==5) { // format xxxmm
                char bkup = s[3];
                s[3] = 0;
                lat_lon=float(atoi(s));
                s[3] = bkup;
                lat_lon += strtod(s+3, NULL) / 60.0f;
            } else {
                lat_lon = 9999;
            }
        }
    }
    if(i==0)
        lat_lon = 9999;
    else if(nsew[0] == 'W' || nsew[0] == 'S')
        lat_lon = -lat_lon;
    return lat_lon;
}

uint32_t parseUTC(char s[])
{   
    // assumes a format. I.e. there must be a string at s of length 9. No sanity checking is performed!
    // hhmmss.ss 
    // 012345678
    uint32_t hundreths = (s[7]-48)*10+(s[8]-48);
    uint32_t seconds = (s[4]-48)*10+(s[5]-48);
    uint32_t minutes = (s[2]-48)*10+(s[3]-48);
    uint32_t hours = (s[0]-48)*10+(s[1]-48);
    return hundreths + 100*(seconds + 60*(minutes + 60*hours));
}

/* Parse a NMEA string
 *
 * This function is only safe because I know that a NMEA message passed to this
 * function has (at least) one more char available after len.
 */
void 
ParseNMEA::parse(char buf[], size_t len)
{
    const size_t MAX_N_WORDS = 20;
    char* words[MAX_N_WORDS];
    size_t n_word = 0;
    if(len == 0) { 
        #ifdef DEBUG
        printf("ParseNMEA error: Zero length input\n");
        #endif
        onError(buf, len);
        return;
    }
    words[n_word++] = buf;
    size_t i;
    for(i=0; i<len && buf[i]!='\0'; i++) {
        if(n_word >= MAX_N_WORDS) {
            #ifdef DEBUG
            printf("ParseNMEA error: Too many words\n");
            #endif
            onError(buf, len);
            return;
        } 
        if(buf[i]==',') {
            buf[i] = 0;
            words[n_word++] = buf+i+1;
        }
    }
    if(n_word == 0) {
        #ifdef DEBUG
        printf("ParseNMEA error: No words\n");
        #endif
        onError(buf, len);
        return;
    }
    if(strcmp(words[0], "GPGGA")==0 || strcmp(words[0], "GNGGA")==0) {
        if(n_word != 15) {
            #ifdef DEBUG
            printf("ParseNMEA error: %s message number of words is %lu, should be %d\n", words[0], n_word, 15);
            #endif
            return;
        }
        uint32_t utc = words[1][0] != '\0' ? parseUTC(words[1]) : 0;
        float lat = parseLatLon(words[2], words[3]);
        float lon = parseLatLon(words[4], words[5]);   
        uint8_t qual = words[6][0]-48;  // one digit 0..9
        uint8_t n_satellites = strtof(words[7], NULL);
        float   hdil = strtof(words[8], NULL);
        float   alt = strtof(words[9], NULL);
        float   height = strtof(words[11], NULL);
        onGGA(utc, lat, lon, qual, n_satellites, hdil, alt, height);
    } else {
        #ifdef DEBUG
        printf("ParseNMEA error: Unknown NMEA message %s\n", words[0]);
        #endif
        onError(buf, len); 
    }
}

enum Quality {
    NoFix = 0,
    StandardGPS = 1,
    DifferentialGPS = 2,
    RTKFixedSolution = 4,
    RTKFloatSolution = 5,
    EstimatedFix = 6
};


#endif /* __PARSENMEA_H__ */
