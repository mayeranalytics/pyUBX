#!/usr/bin/env python3
"""Scan the output produced by UBX.py --NMEA and transform it back into
proper NMEA with $ and * and checksum. This output can then be used with other
tools."""

import UBX
from UBXManager import UBXManager
import sys


def NMEAChkSum(line):
    """Return NMEA checksum of line as a string."""
    chksum = 0
    for c in line:
        chksum ^= ord(c)
    return '{:02x}'.format(chksum)

if len(sys.argv) < 2:
    sys.stderr.write("Usage:\n  parse_NMEA_log.py FILENAME\n")
    sys.exit(1)

filename = sys.argv[1]
file = open(filename, "r")

errCount = 0
for line in file.readlines():
    try:
        [dt, NMEA] = line.strip().split(" ")
    except:
        errCount += 1
    NMEA = "${}*{}".format(NMEA, NMEAChkSum(NMEA))
    print(NMEA)

if errCount:
    sys.stderr.write("Found {} bad lines.\n".format(errCount))
