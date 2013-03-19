import autowrap.Code


def test():
    Code = autowrap.Code.Code
    c = Code()
    c.add("def $name(x):", name="fun")

    inner = Code()
    inner.add("""if x
                + == 3:
                |    return
                + 4
              """)
    inner.add("else:")

    inner2 = Code()
    inner2.add("""return
                 + 2*x""")

    inner.add(inner2)

    c.add(inner)

    result = c.render()
    lines = [ line.rstrip() for line in result.split("\n")]
    assert lines[0] == "def fun(x):",      repr(lines[0])
    assert lines[1] == "    if x == 3:",   repr(lines[1])
    assert lines[2] == "        return 4", repr(lines[2])
    assert lines[3] == "    else:",        repr(lines[3])
    assert lines[4] == "        return 2*x", repr(lines[4])
    assert len(lines) == 5




