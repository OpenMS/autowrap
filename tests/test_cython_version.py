from Cython.Compiler.Version import version as cython_version


def test_cython_version_at_least_3_1() -> None:
    version_parts = str(cython_version).split(".")
    major = int(version_parts[0])
    minor = int(version_parts[1]) if len(version_parts) > 1 else 0
    assert major > 3 or (major == 3 and minor >= 1), (
        f"Expected Cython >= 3.1, but found {cython_version}"
    )

