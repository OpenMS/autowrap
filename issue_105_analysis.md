# Analysis of Issue #105: Static Function Wrapping Bug

**Issue:** https://github.com/OpenMS/autowrap/issues/105
**Title:** "wrapping static functions as non-static ones doesn't cause an error"
**Created:** May 21, 2021
**Analysis Date:** January 2026

## Summary

**Status: STILL CURRENT** - The issue remains valid. There is no validation to detect mismatches between PXD declarations and actual C++ static/non-static methods.

## Background

The issue reports that developers can mistakenly wrap static C++ functions as non-static Python methods (or vice versa) without receiving any error or warning. The generated wrappers will silently fail at runtime.

## Technical Analysis

### How Static Methods Are Currently Handled

1. **Detection (PXDParser.py:581-584)**
   ```python
   if node.decorators is not None:
       for dec in node.decorators:
           if dec.decorator.name == "staticmethod":
               is_static = True
   ```
   The `is_static` flag is derived **solely** from the `@staticmethod` decorator in the PXD file.

2. **Code Generation (CodeGenerator.py:1240-1262, 1427-1434)**
   - If `is_static=True`: Adds `@staticmethod` decorator and generates `ClassName.method()` call
   - If `is_static=False`: Generates `self.inst.get().method()` call

3. **No C++ Parsing**
   Autowrap **does not parse C++ headers**. It relies entirely on PXD file declarations. The `cdef extern from "foo.hpp"` statement only specifies where the implementation exists, but autowrap doesn't inspect the C++ code for the `static` keyword.

### What Was Fixed in PR #115

PR #115 (merged January 2022) added **support for** the `@staticmethod` decorator in PXD files. This allows users to correctly declare static methods, but it **did not add validation** to detect incorrect declarations.

### The Remaining Problem

There is **no validation** that checks:
1. If a method marked with `@staticmethod` in PXD is actually static in C++
2. If a method without `@staticmethod` in PXD is actually static in C++ (causing silent failures)

### Failure Scenarios

| PXD Declaration | C++ Reality | Result |
|-----------------|-------------|--------|
| `@staticmethod` | static | Correct |
| No decorator | non-static | Correct |
| `@staticmethod` | non-static | Cython compile error (calling non-static via class name) |
| No decorator | static | **Silent failure** - may compile but behave incorrectly |

The fourth scenario is the most problematic: calling a static method via `self.inst.get()` is valid C++ syntax, so it may compile but produce unexpected behavior or confusing error messages at runtime.

## Recommendations

### Option 1: Documentation Warning (Low Effort)
Add documentation warning users to carefully verify static method declarations match C++ declarations.

### Option 2: Runtime Warning (Medium Effort)
Add a compile-time or runtime warning when methods don't work as expected. However, this is difficult without C++ parsing.

### Option 3: C++ Header Parsing (High Effort)
Implement optional C++ header parsing (using libclang or similar) to validate PXD declarations against actual C++ code. This would be a significant undertaking but would catch many categories of declaration mismatches.

### Option 4: Test Generation (Medium Effort)
Generate test stubs that exercise each wrapped method to catch failures early in the development cycle.

## Files Examined

- `autowrap/PXDParser.py` - Static method detection (lines 515-606)
- `autowrap/DeclResolver.py` - Method resolution (lines 228-230, 634)
- `autowrap/CodeGenerator.py` - Code generation (lines 1215-1434)
- `tests/test_files/templated.pxd` - Test case with static method

## Conclusion

Issue #105 is **still current and valid**. While PR #115 added proper support for the `@staticmethod` decorator, there is no mechanism to validate that declarations match reality. Users must manually ensure their PXD static method declarations accurately reflect the C++ implementation.
