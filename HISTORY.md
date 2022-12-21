autowrap 0.22.7

- automatically generates pyi typestubs next to the pyx files


autowrap 0.22.8

- Added support for missing operators '-', '/', '-=', '*=', '/='
- Refactored special method generation a little, with minor fixes.
- Finished complete support for type stubs for all? generated Cython code

autowrap 0.22.9

- Typing of a majority of classes and functions of the codebase
- Requires python 3.7 instead of 3.6 now
- Support for "const Members" as alternative to "wrap-constant" (experimental)

autowrap 0.22.10

- Revamped docstrings for overloaded methods in generated pyx files. They use RST and sphinx.autodoc syntax now.

autowrap 0.22.11

- Fixes some issues with typing support on python side
- Added a real C++ bool converter. C++ bools in a pxd will now be real booleans
  on python side. Not "just" ints and will also be typed like that.
