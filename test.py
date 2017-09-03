#!/usr/bin/env python3
"""TODO."""

import sys
import os
import UBX

if __name__ == '__main__':

    setPMS = UBX.CFG.PMS.Set(powerSetupValue=2).serialize()
    print(setPMS)
