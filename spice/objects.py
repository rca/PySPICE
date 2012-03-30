# Released under the BSD license, see LICENSE for details

class DataType(object):
    def __init__(self):
        self.SPICE_CHR = 0
        self.SPICE_DP = 1
        self.SPICE_INT = 2
        self.SPICE_TIME = 3
        self.SPICE_BOOL = 4


class Cell(object):
    CellDataType = DataType

    def __init__(self, arg):
        self.dtype = self.CellDataType()
        self.length = 0
        self.size = 0
        self.card = 0
        self.isSet = False
        self.adjust = False
        self.init = False
        self.base = None # this is a void *; how to represent it?
        self.data = None # this is a void *; how to represent it?


class Ellipse(object):
    """Class representing the C struct SpiceEllipse"""
    def __init__(self, center=None, semi_major=None, semi_minor=None):
        self.center = center or [0.0] * 3
        self.semi_major = semi_major or [0.0] * 3
        self.semi_minor = semi_minor or [0.0] * 3

    def __repr__(self):
        return '<SpiceEllipse: center = %s, semi_major = %s, semi_minor = %s>' % \
            (self.center, self.semi_major, self.semi_minor)


# EK Attribute Description
class EkAttDsc(object):
    def __init__(self):
        self.cclass = 0
        self.dtype = DataType()
        self.strlen = 0
        self.size = 0
        self.indexd = False
        self.nullok = False

# EK Segment Summary
class EkSegSum(object):
    def __init__(self):
        self.tabnam = ''
        self.nrows = 0
        self.ncols = 0
        self.cnames = [] # list of strings
        self.cdescrs = [] # list of EkAttDsc


class Plane(object):
    def __init__(self, normal=[0.0]*3, constant=0.0):
        self.normal = normal
        self.constant = constant

    def __str__(self):
        return '<Plane: normal=%s; constant=%s>' % (', '.join([str(x) for x in self.normal]), self.constant)

