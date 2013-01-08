#!/usr/bin/env python
#
# Select and extract JPL/NAIF SPICE toolkit for local OS and Architecture
#
# Run this command to extract appropriate JPL/NAIF SPICE toolkit
# into ./cspice/:
#
#   getnaiftoolkit.py extract
#
# Author: Brian Carcich, drbitboy@gmail.com
# Original date:  2013-01-05
#
# Released under the BSD license, see LICENSE for details
#
# $Id$

"""
getnaiftoolkit.py

Extracts JPL/NAIF SPICE toolkit from compressed URL stream of

  cspice.tar.Z

N.B. Untested for Windows/VisualC, cspice.zip

Usage:  

  % python getnaiftoolkit.py [extract] [topdir=subdir/] [test=MACH_OS_COMPILER_NNbit]

  ### default sys.argv[1] is tv => tar tvf -, so
  ###
  ###   python getnaiftoolkit.py | more
  ###
  ### is probably a good idea

In Python:

  import getnaiftoolkit
  getnaiftoolkit.main(['extract'])

"""
import re
import os
import sys
import urllib
import subprocess

########################################################################
def getnstkurl(force=None,log=False):
  """
Select URL of NAIF SPICE toolkit cspice.tar.Z suitable for
local OS (os.uname()[0]) and architecture (os.uname()[-1])

  OS:  OSX; Cygwin; Linux; Windows; SunOS.

  MACHINE:  i386; x86_64; PowerPC/PPC.

Index of http://naif.jpl.nasa.gov/pub/naif/toolkit/C/:

  - Subdirectories:

  MacIntel_OSX_AppleC_32bit/
  MacIntel_OSX_AppleC_64bit/

  MacPPC_OSX_AppleC_32bit/

  PC_Cygwin_GCC_32bit/

  PC_Linux_GCC_32bit/
  PC_Linux_GCC_64bit/

  PC_Windows_VisualC_32bit/
  PC_Windows_VisualC_64bit/

  SunIntel_Solaris_SunC_32bit/
  SunIntel_Solaris_SunC_64bit/

  SunSPARC_Solaris_GCC_32bit/
  SunSPARC_Solaris_GCC_64bit/
  SunSPARC_Solaris_SunC_32bit/
  SunSPARC_Solaris_SunC_64bit/

  - under those directories are packages/cspice.tar.Z

  """

  ### Convert possible alternate values that may be expected from os.uname()

  convert = dict( DARWIN='OSX'
                , POWERPC='PPC'
                , SOLARIS='SUNOS'
                , I486='I386'
                , I586='I386'
                , I686='I386'
                , I86PC='I386'
                )

  ### Translatiions by OS and MACHINE to first and second elements of SPICE
  ###   subdirectory name e.g. OSX and I386 => MacIntel_OSX; 
  ###   SUNOS and SUN4U => SunSPARC_Solaris
  ###
  
  dSys1 = dict( OSX=dict( I386='MacIntel', PPC='MacPPC', sis2='OSX', zSfx='tar.Z' )
              , LINUX=dict( I386='PC', X86_64='PC', sis2='Linux', zSfx='tar.Z' )
              , CYGWIN=dict( I386='PC', X86_64='PC', sis2='Cygwin', zSfx='tar.Z' )
              , WINDOWS=dict( I386='PC', X86_64='PC', sis2='Windows', zSfx='zip' )
              , SUNOS=dict( I386='SunIntel', SUN4U='SunSPARC', sis2='Solaris', zSfx='tar.Z' )
              )

  ### Suffix:  32bit or 64bit:

  lsmi=len(str(sys.maxint))

  ### 32-bit architecture will have sys.maxint = 2^32 - 1 ~  2G = 10 digits
  ### 64-bit architecture will have sys.maxint = 2^64 - 1 ~ 16E = 19 digits

  if lsmi<11: unbit='32bit'
  elif lsmi<20: unbit='64bit'

  ### Use os.uname() to get OS and MACHINE:

  un=os.uname()

  opsys = (''.join(un[0].split())).upper()
  machine = (''.join(un[-1].split())).upper()

  if opsys in convert: opsys=convert[opsys]
  if machine in convert: machine=convert[machine]

  ### Chop to six characters to simplify CYGWIN_NT...

  opsys=opsys[:6]

  if opsys=='OSX':
    compiler='AppleC'

  elif opsys=='WINDOWS':
    compiler='VisualC'

  elif opsys=='LINUX' or opsys=='CYGWIN':
    compiler='GCC'

  elif opsys=='SUNOS':

    ### For Solaris, assume SunC compiler ...
    compiler='SunC'

    ### ... unless gcc found in PATH
    for path in os.environ['PATH'].split(':'):
      if os.path.exists( os.path.join(path,'gcc')):
        compiler='GCC'
        break

    ### No toolkit exists for GCC on Solaris/x86, so force SunC
    if dSys1[opsys][machine] == 'SunIntel': compiler='SunC'

  ### Build the subdirectory name ...

  subdir='_'.join([ dSys1[opsys][machine], dSys1[opsys]['sis2'], compiler, unbit ])

  fullurl = os.path.join( 'http://naif.jpl.nasa.gov/pub/naif/toolkit/C/', subdir, 'packages', 'cspice.'+ dSys1[opsys]['zSfx'] )

  if not (force is None):
    M,O,C,B = [s.upper() for s in force.split('_')]
    oldurl = fullurl
    fullurl = os.path.join( 'http://naif.jpl.nasa.gov/pub/naif/toolkit/C/', force, 'packages', 'cspice.'+ dSys1[O]['zSfx'] )
    if log:  sys.stderr.write( '### Overriding %s with %s\n' % (oldurl,fullurl,) )

  ### ... and return the full URL

  return fullurl

########################################################################
def main(argv):
  """
  getnaiftoolkit.main()

  Use getnstkurl() above to stream cspice.tar.Z or .zip from JPL/NAIF
  website into 'gunzip | tar ?f - [-C subdir/] cspice/' for
  non-Windows systems, or into StringIO => ZipFile for Windows

  - do no use tar z.f - as it will not work on Solaris

  Arguments:

    argv:  list, or tuple, of strings, equivalent to typical sys.argv

    - list                   - list cspice/ files in cspice.{tar.gz,zip}
    - extract                - extract cspice/ files from cspice.{tar.gz,zip}
    - topdir=dir/subdir/     - extract files to .../
    - test=MACH_OS_CC_NNbit  - extract files to .../
  """

  actionOption='list'
  topdirOption='./'
  testOption=None

  for arg in argv:
    if arg=='extract': actionOption='extract' ; continue
    if arg=='list': actionOption='list' ; continue
    if arg[:7]=='topdir=': topdirOption=arg[7:] ; continue
    if arg[:5]=='test=': testOption=arg[5:] ; continue

  ### Get URL and open as stream

  nstkurl = getnstkurl(force=testOption,log=True)
  zurl = urllib.urlopen( nstkurl )

  if nstkurl[-4:].lower()=='.zip':

    ### If URL is a .ZIP file, read entire file into StringIO buffer
    ### and use zipfile.ZipFile to extract cspice/

    import zipfile
    from StringIO import StringIO

    sys.stderr.write( "### Downloading %s this may take a while ..." % (nstkurl,) )
    sys.stderr.flush()

    zf = zipfile.ZipFile(StringIO(zurl.read()))

    sys.stderr.write( " download complete; %sing files from cspice/ ...\n" % (actionOption,) )
    sys.stderr.flush()

    for info in zf.infolist():
      filepath=info.filename
      if os.path.dirname(filepath)[:7]=='cspice/':
        if actionOption=='list':
          print( os.path.join( topdirOption, filepath ) )
        elif actionOption=='extract':
          zf.extract(member=filepath,path=topdirOption)

    print( "### %sing complete" % (actionOption,) )

  else:
    ### If URL is not a .ZIP file, assume it is .tar.Z, and
    ### extract data with pipe to subprocess ( gunzip | tar ..f - ) 

    ### Build subprocess command

    tarAction=dict( list='tv', extract='x')[actionOption]
    cmd = '( gunzip | tar %sf - %s )' % (tarAction,'-C '+topdirOption,)

    sys.stderr.write( '### Executing command "%s" on URL \n### %s\n###' % (cmd,nstkurl,) )

    ### Spawn 'gunzip|tar' subproces

    process = subprocess.Popen( cmd, shell=True, stdin=subprocess.PIPE )

    ### Read 10k compressed characters => every 100 reads will be ~1MB
    ### Since cspice.tar.Z ranges from 20MB to 36MB, there will be
    ###   less than 4000 reads.

    n = 4000

    ### Read 10k compressed characters at a time and pass them to
    ###   subprocess (gunzip|tar)

    zs = zurl.read(10240)
    while len(zs)>0:
      process.stdin.write( zs )

      if (n%100)==0:
        sys.stderr.write( ' %d' % (n/100,) )
        sys.stderr.flush()
      n -= 1
      zs = zurl.read(10240)

  print( '### Done' )

  zurl.close()

########################################################################
if __name__=="__main__":
  """
  Usage:  python getnaiftoolkit.py [extract [topdir=subdir/]]
  """
  main(sys.argv[1:])
