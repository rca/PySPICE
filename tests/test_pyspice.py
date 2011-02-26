# Released under the BSD license, see LICENSE for details

import os, sys, unittest
from spice import Ellipse, Plane

class TestFile(unittest.TestCase):
    def testEllipse(self):
        center = [234.3, 8348.3, 937.6]
        semi_major = [5.0, 293.4, 11.0]
        semi_minor = [6.0, 3.0, 6.0]

        ellipse = Ellipse(
            center=center,
            semi_minor=semi_minor,
            semi_major=semi_major
        )

        self.assertTrue(ellipse.center == center)
        self.assertTrue(ellipse.semi_minor == semi_minor)
        self.assertTrue(ellipse.semi_major == semi_major)

    def testPlane(self):
        normal = [2.4, 34.5, 9.2]
        constant = 4.7

        p = Plane(normal, constant)

        self.assertTrue(p.normal == normal)
        self.assertTrue(p.constant == constant)


if __name__ == '__main__':
    unittest.main()
