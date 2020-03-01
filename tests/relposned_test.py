import unittest

from IPython.testing.tools import make_tempfile

import ubx
from pathlib import Path
import time
import queue
import tempfile

class RelposnedTest(unittest.TestCase):
    def test_binfile(self):
        """ Test the binary file with 4 PVT & RELPOSNED pairs of records from a
        uBlox-F9P paired with another F9P to form a GPS compass.
        The first pair is before the GPS fully locked on.  The remaining 3
        are after a gap in time to let the GPS eliminate carrier ambiguity
        """
        testfile = Path(__file__).parent.joinpath("testdata", "relposned_test.bin")
        nmsg = 8
        ubxq = ubx.UBXQueue(ser=testfile.open("rb"), start=True, eofTimeout=0)
        # Read and test
        time.sleep(1)
        self.assertFalse(ubxq.empty())
        msgs = []
        for i in range(nmsg):
            msgs.append(ubxq.get(block=True, timeout=1))
        # Make sure there is nothing more to read
        self.assertTrue(ubxq.empty())
        try:
            ubxq.get(block=True, timeout=0.1)
            self.assertFalse()
        except queue.Empty as e:
            pass

        # Check that the messages are the same both as summaries and pretty-prints.
        testascii = testfile.parent.joinpath(testfile.stem+'.txt')
        testasciiout = Path(tempfile.mktemp(testascii.stem))
        print("Writing ",testasciiout)
        fout = testasciiout.open("w")
        for m in msgs:
            print(m.summary())
            print(m.summary(), file=fout)
            fout.write(m.__str__()+"\n\n")
        fout.close()
        strings = []
        for fname in (testasciiout, testascii):
            with fname.open() as f:
                strings.append(f.read())
        self.assertEqual(*strings)


if __name__ == '__main__':
    unittest.main()
