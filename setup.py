# the following  import fixes/avoids some nostests issue
# see

try:
    import multiprocessing
except ImportError:
    pass

# the follwing is standard setup.py for a single package 'autowrap'

from setuptools import setup, find_packages

import autowrap

version = '%s.%s.%s' % autowrap.version

setup(name="autowrap",
      version=version,
      maintainer="Uwe Schmitt",
      maintainer_email="uschmitt@mineway.de",
      license="http://opensource.org/licenses/BSD-3-Clause",
      platforms=["any"],
      description='Generates Python Extension modules from commented Cython PXD files',
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python :: 2.7",
                   "Topic :: Software Development :: Code Generators",
                   ],
      long_description="""
autowrap automatically generates python extension modules for wrapping
C++ libraries based on annotated (commented) cython pxd files. """,

      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,   # see MANIFEST.in
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      install_requires=['Cython>=0.18'],
      entry_points={
           'console_scripts':
           [
               'autowrap = autowrap.Main:main',
           ]
      },

     )
