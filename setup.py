# the following  import fixes/avoids some nostests issue
# see http://bugs.python.org/issue15881

try:
    import multiprocessing
except ImportError:
    pass

# the follwing is standard setup.py for a single package 'autowrap'

from setuptools import setup, find_packages

version = '0.1'

setup(name="autowrap",
      version=version,
      description='Generates Python Extension modules from Cython PXD files',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      #package_data = { 'autowrap' :  ["data_files/boost/*",],
                       #"" : [ "autowrap/data_files/boost/*"]
                       #},
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points={
           'console_scripts':
           [
               'autowrap = autowrap.Main:main',
           ]
      },
      install_requires=["cython", ],
      setup_requires=["nose", ],

     )
