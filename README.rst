SPICE toolkit Python Module
===========================

Python wrapper around the NAIF CSPICE library.  Released under the BSD license, see LICENSE for details.

Building PySPICE
----------------

First, download the cspice toolkit and extract it to the directory "cspice" in
this directory right alongside the setup.py file.  Once the cspice source is
there, run setup.py like so::

  python setup.py build_ext

Then install::

  python setup.py install

64 bit vs 32 bit
----------------
CSPICE is published in both 64 and 32 bit versions. Make sure that you compile
PySPICE with a Python bit architecture that fits to the CSPICE you have
downloaded, otherwise you will get warnings at compile time (not so bad) and
errors of missing links in the library at run time (basically, you can't *import
spice*.

Manual Instructions
-------------------
Though it shouldn't be necessary, here are the old step-by-step instructions.

In order to build this module, first generate the extension code using the
mkwrapper.py script.  This is done running mkwrapper.py with the path to the
CSPICE toolkit directory as an argument and redirecting the output to
"spicemodule.c"::

  python mkwrapper.py /path/to/cspice > spicemodule.c

Once the C file is generated, the module can be compiled::

  python setup.py build_ext -I/path/to/cspice/include -L/path/to/cspice/lib

Then the module can be installed using::

  python setup.py install --prefix=/installation/path

If the installation path used is not standard, add the path to your
``PYTHONPATH`` environment variable.  In bash::

  export PYTHONPATH=/installation/path/lib/python<version>/site-packages:${PYTHONPATH}

or *csh::

  setenv PYTHONPATH /installation/path/lib/python<version>/site-packages:${PYTHONPATH}

Usage
=====

  berto:~$ python
  Python 2.4.2 (#2, Sep 30 2005, 21:19:01)
  [GCC 4.0.2 20050808 (prerelease) (Ubuntu 4.0.1-4ubuntu8)] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>> from spice import *
  >>> furnsh("/home/berto/tmp/insitu/kernels/load.mk")
  >>> utc2et("2004-06-11T19:32:00")
  140254384.18462521

Some things to keep in mind
---------------------------

The python wrapper drops the _c suffix in all function names, so the
function utc2et_c becomes utc2et.

Also, the CSPICE toolkit passes both inputs and outputs into a SPICE
function::

  SpiceDouble et;
  SpiceChar * utc = "2004-06-11T19:32:00";

  utc2et_c(utc, &et);

  printf("et: %f\n", et);

But, in Python, the outputs are returned::

  utc = "2004-06-11T19:32:00"

  et = utc2et(utc)

  print "et: %f" % et

If a function returns multiple values they are returned in a tuple::

  target_pos, light_time = spkpos(target, sc_et, frame, aberration, sc_name)

  print "light time: %f" % light_time
  print "xyz: [%e, %e, %e]" % target_pos

In the case above, the target position and light time are returned in a tuple.
Additionally, target_pos itself is a tuple; its individual elements can be
accessed like this::

  print "x position: %d" % target_pos[0]

Tuples act just like arrays.

Enjoy!
