from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'segmentation function',
  ext_modules = cythonize("segment.pyx"),
)
