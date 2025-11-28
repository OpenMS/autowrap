from Cython.Compiler.Version import version as cython_version


def test_cython_major_version_at_least_3() -> None:
    major_str = str(cython_version).split(".")[0]
    assert int(major_str) >= 3

