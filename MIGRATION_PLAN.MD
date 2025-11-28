## Migration Plan: Cython 3+ Only

This document outlines how to drop legacy Cython 0.x / “Cython 2-style”
compatibility and make `autowrap` cleanly target Cython 3+.

### 1. Tighten Cython Version Requirements

- Update `pyproject.toml` to require Cython 3+ (for example
  `Cython>=3.0` instead of `Cython>=0.19`).
- Optionally add a runtime guard that checks
  `Cython.Compiler.Version.version` and raises a clear error if it is
  `< 3`.

### 2. Simplify `PXDParser` for Cython 3 Only

Key points:

- `autowrap/PXDParser.py:406–418`:
  conversion of `node.templates` from `[(string, bool)]` to `[string]`
  is still used and matches current Cython 3 behavior, so it remains.
- `autowrap/PXDParser.py:627–632`:
  legacy `options.create_context()` (Cython 0.x) use has been removed in
  favor of `Context.from_options(options)` (Cython 3).

Planned/implemented changes:

- Assume the Cython 3 AST / options API:
  - Keep the `template_parameters` conversion as an internal
    normalization step for template arguments.
  - Unconditionally use `Context.from_options(options)` (or the
    canonical Cython 3 way to construct a `Context`).
- Keep or simplify `options.language_level`:
  - Currently set to `sys.version_info.major`; optionally hard-code to
    `3` if we want explicit Python 3 semantics everywhere.

### 3. Simplify `run_cython` (CLI) to Cython 3 Only

Current compatibility code in `autowrap/Main.py:176–188`:

- Tries `from Cython.Compiler.Options import directive_defaults`,
  falls back to `Cython.Compiler.Options.get_directive_defaults()` for
  Cython 0.25.
- Commented as “for backwards-compat to Cython 0.X”.

Planned changes:

- Assume Cython 3+:
  - Drop the `try/except ImportError` and always import
    `directive_defaults` from `Cython.Compiler.Options`.
  - Remove the fallback call to `get_directive_defaults()`.
- Revisit directives (behavior, not compatibility):
  - Decide whether `binding=False` should be kept or whether Cython 3
    defaults are sufficient.
  - Keep `boundscheck=False`, `wraparound=False`, and the chosen
    `language_level` setting.

### 4. Clean Up Tests Assuming Cython < 3

Current version-specific logic:

- `tests/test_code_generator.py:test_enums`:
  - Imports `cython_version` from `Cython.Compiler.Version`.
  - Returns early if `int(cython_version[0]) < 3`.

Planned changes:

- Remove the version check and the `cython_version` import so that
  `test_enums` always runs (since Cython 3+ is now the minimum).
- If any other tests gate behavior on “Cython < 3”, remove those
  branches as well.

### 5. Address `language_level=2` Test Files

Many test `.pxd` / `.pyx` files currently include:

- `# cython: language_level=2` (e.g. `tests/test_files/minimal.pxd`,
  `A.pxd`, `B.pxd`, `C.pxd`, `D.pxd`, `Cycle0/1/2.pxd`,
  `libcpp_test.pxd`, `templated.pxd`, `base*.pxd`,
  `int_container_class.pxd`, `gil_testing.pxd`, etc.).
- Some `.pyx` files rely on Python 2 syntax (e.g.
  `print "dealloc called"` in `tests/test_files/itertest.pyx`).

Options:

- **Option A (fully modernize)**:
  - Remove `language_level=2` pragmas and rely on the global
    `language_level` from `directive_defaults` (Python 3 semantics).
  - Update any Python 2-only syntax in test files to Python 3 syntax
    (e.g. use `print("…")`).
  - Confirm that the C AST expected by `PXDParser` is unchanged for
    these declarations.
- **Option B (keep as historical fixtures)**:
  - Leave `language_level=2` pragmas if they still compile under
    Cython 3 and if Python 2 semantics in tests are acceptable.
  - This keeps autowrap itself Cython 3-only while tolerating older
    directives in test fixtures.

If the goal is “fully Cython 3 / Python 3 semantics everywhere”,
Option A should be implemented.

### 6. Refresh Docs and Examples for Cython 3

Not strictly required for compatibility, but desirable for clarity:

- `example/setup.py` and `tests/test_full_library.py` use
  `from Cython.Distutils import build_ext`; this still works under
  Cython 3, but more modern examples might use `cythonize`.
- `docs/README.md` and `README.md` may include Python 2-style code
  snippets or wording that implicitly references “Cython 0.X”.

Planned changes:

- Update documentation to state that autowrap targets Cython 3+.
- Modernize any Python 2-style examples (e.g. `print` statements) to
  Python 3 syntax where appropriate.
- Optionally update example build instructions to show idiomatic
  Cython 3 usage.

### 7. Verification After Changes

After applying the above steps:

- Run the full test suite under Cython 3.x:
  - `pytest -v` from the project root.
  - Ensure all tests run (no early returns based on Cython version).
- Optionally add a small test or import-time assertion that:
  - Checks `int(Cython.Compiler.Version.version[0]) >= 3`, and
  - Fails fast if someone accidentally runs under an older Cython.

This will ensure that autowrap’s parser, code generator, and CLI are
all consistently using Cython 3 APIs and Python 3 semantics.
