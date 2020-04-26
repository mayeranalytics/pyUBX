#!/usr/bin/env python3
"""Scan the output produced by UBXtool.py --NMEA and transform it back into
proper NMEA with $ and * and checksum. This output can then be used with other
tools."""

import sys


def NMEAChkSum(line):
    """Return NMEA checksum of line as a string."""
    chksum = 0
    for c in line:
        chksum ^= ord(c)
    return '{:02x}'.format(chksum)

def parse_NMEA_log_main():
    if len(sys.argv) < 2:
        sys.stderr.write("Usage:\n  {} FILENAME\n\n".format(sys.argv[0]) + __doc__)
        sys.exit(1)

    with open(sys.argv[1], "r") as file:

        errCount = 0
        for line in file.readlines():
            try:
                [dt, NMEA] = line.strip().split(" ")
            except:
                errCount += 1
            else:
                print("${}*{}".format(NMEA, NMEAChkSum(NMEA)))

        if errCount:
            sys.stderr.write("Found {} bad lines.\n".format(errCount))

if __name__ == '__main__':
    parse_NMEA_log_main()