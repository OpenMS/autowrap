autowrap 0.22.11

- Fixes some issues with typing support on python side
- Added a real C++ bool converter. C++ bools in a pxd will now be real booleans
  on python side. Not "just" ints and will also be typed like that.