from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'segmentation functions',
  ext_modules = cythonize("segment.pyx"),
)
