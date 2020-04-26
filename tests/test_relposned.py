import unittest

import ubx
from pathlib import Path
import time
import queue
import tempfile

class RelposnedTest(unittest.TestCase):
    def test_binfile(self):
        """ Test the binary file with PVT & RELPOSNED(v1) records.
        Data from a uBlox-F9P paired with another F9P to form a GPS compass.
        The first PVT-RELPOSNED pair is before the GPS fully locked on.  The remaining 3
        are after a gap in time to let the GPS eliminate carrier ambiguity.
        """
        testfname = Path(__file__).parent.joinpath("testdata", "relposned_test.bin")
        nmsg = 8
        testfile = testfname.open("rb")
        ubxq = ubx.UBXQueue(ser=testfile, start=True, eofTimeout=0)
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
        testascii = testfname.parent.joinpath(testfname.stem+'.txt')
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
        testfile.close()
        ubxq.join()



if __name__ == '__main__':
    unittest.main()
