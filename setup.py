# encoding: utf-8
# the following  import fixes/avoids some nosetests issue

try:
    import multiprocessing
except ImportError:
    pass

from setuptools import find_namespace_packages, setup

versionfile = "autowrap/version.py"
exec(open(versionfile).read())

setup(
    name="autowrap",
    version="%d.%d.%d" % __version__,
    maintainer="OpenMS Inc.",
    maintainer_email="webmaster@openms.de",
    license="BSD-3-Clause",
    platforms=["any"],
    description="Generates Python Extension modules from commented Cython PXD files",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
    ],
    long_description="""
autowrap automatically generates python extension modules for wrapping
C++ libraries based on annotated (commented) cython pxd files. """,
    packages=find_namespace_packages(
        include=["autowrap*"],
        exclude=[
            "autowrap.data_files.examples",
            "autowrap.data_files.tests",
            "autowrap.data_files.ez_setup",
        ],
    ),
    include_package_data=True,  # see MANIFEST.in
    zip_safe=False,
    test_suite="nose.collector",
    install_requires=["Cython>=0.19", "setuptools"],
    entry_points={"console_scripts": ["autowrap = autowrap.Main:main"]},
)
