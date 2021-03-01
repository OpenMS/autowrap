# encoding: utf-8
# the following  import fixes/avoids some nostests issue
# see

try:
    import multiprocessing
except ImportError:
    pass

from setuptools import find_packages, setup


VERSION = (0, 22, 3)
# DO NOT FORGET TO BUMP THE VERSION IN version.py !!!!!!!!!!!!!!!!!!!


setup(
    name="autowrap",
    version="%d.%d.%d" % VERSION,
    maintainer="Uwe Schmitt",
    maintainer_email="uschmitt@mineway.de",
    license="http://opensource.org/licenses/BSD-3-Clause",
    platforms=["any"],
    description="Generates Python Extension modules from commented Cython PXD files",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Code Generators",
    ],
    long_description="""
autowrap automatically generates python extension modules for wrapping
C++ libraries based on annotated (commented) cython pxd files. """,
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,  # see MANIFEST.in
    zip_safe=False,
    test_suite="nose.collector",
    install_requires=["Cython>=0.19"],
    entry_points={"console_scripts": ["autowrap = autowrap.Main:main"]},
)
