import os

from distutils.core import setup, Extension

APP_NAME = os.path.basename(os.getcwd())
SHARE_DIR = os.path.join('share', 'spicedoc')

module1 = Extension(
    '_spice',
    sources = ['pyspice.c', 'spicemodule.c'],
	libraries = ['cspice'],
)

setup(
    name = 'Spice',
    version = '1.0',
    description = 'Spice Wrapper Module',
    packages = ['spice'],
    ext_modules = [module1]
)
