from sysinfo import free_mem
import contextlib
import sys
import os


def show_mem(label):

    p = free_mem()
    p /= 1024.0 * 1024
    print(label + " ").ljust(50, "."), ": %8.2f MB" % p
    sys.stdout.flush()


@contextlib.contextmanager
def MemTester(name, use_assert=False):
    mem_at_start = free_mem()
    print
    show_mem("start test '%s' with" % name)
    yield
    missing = mem_at_start - free_mem()
    show_mem("end with")
    print
    if use_assert:
        assert missing < 0.1 * mem_at_start, "possible mem leak"


def test00():

    import autowrap

    source_files = os.path.join(os.path.dirname(__file__), "source_files")

    target = os.path.join(source_files, "chunk_wrapper.pyx")

    autowrap.parse_and_generate_code(
        "chunk.pxd", root=source_files, target=target, debug=True
    )

    wrapped = autowrap.Utils.compile_and_import(
        "chunk_wrapped", [target], [source_files]
    )

    os.remove(target)
    assert wrapped.__name__ == "chunk_wrapped", wrapped.__name__
    with MemTester("all", use_assert=True):
        with MemTester("one"):
            li = []
            for i in range(10000):
                li.append(wrapped.Chunk(0))

        with MemTester("two"):
            li = []
            for i in range(10000):
                li.append(wrapped.Chunk(0).getCopy())
        with MemTester("three"):
            li = []
            for i in range(100):
                li.extend(wrapped.Chunk(0).create(100))
        del li
