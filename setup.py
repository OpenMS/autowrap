# encoding: utf-8
# the following  import fixes/avoids some nosetests issue

try:
    import multiprocessing
except ImportError:
    pass

from setuptools import find_packages, setup

versionfile = "autowrap/version.py"
try:
    execfile(versionfile)
except:
    exec(open(versionfile).read())

setup(
    name="autowrap",
    version="%d.%d.%d" % __version__,
    maintainer="The OpenMS team and Uwe Schmitt",
    maintainer_email="uschmitt@mineway.de",
    license="http://opensource.org/licenses/BSD-3-Clause",
    platforms=["any"],
    description="Generates Python Extension modules from commented Cython PXD files",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Code Generators",
    ],
    long_description="""
autowrap automatically generates python extension modules for wrapping
C++ libraries based on annotated (commented) cython pxd files. """,
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,  # see MANIFEST.in
    zip_safe=False,
    test_suite="nose.collector",
    install_requires=["Cython>=0.19", "setuptools"],
    entry_points={"console_scripts": ["autowrap = autowrap.Main:main"]},
)
