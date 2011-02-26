from unittest import TestCase

import spice

class ExceptionTestCase(TestCase):
    def test_raise_spice_exception(self):
        def raise_it():
            raise spice.SpiceException('testing')

        self.assertRaises(spice.SpiceException, raise_it)

    def test_spice_exception(self):
        self.assertRaises(spice.SpiceException, spice.furnsh, '/dev/null')
