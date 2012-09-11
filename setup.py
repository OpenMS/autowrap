from setuptools import setup, find_packages

version = '0.1'

setup(name="autowrap",
      version=version,
      description='Generates Python Extension modules from Cython PXD files',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
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
