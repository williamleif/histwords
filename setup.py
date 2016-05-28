from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    name = "Langchange",
    ext_modules = cythonize(["googlengram/pullscripts/*.pyx", "cooccurrence/*.pyx"]),
    include_dirs = [numpy.get_include()]
)
