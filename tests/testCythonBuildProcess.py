import os
import autowrap.Utils


def setup():
    assert os.environ.get("VIRTUAL_ENV") != None, "PLEASE RUN THIS TEST IN"\
                                                  "VIRTUAL ENV !!!"

test_files = os.path.join(os.path.dirname(__file__), 'test_files')

def testBuildExt():
    pyx_file = os.path.join(test_files, "itertest.pyx")
    itertest = autowrap.Utils.compile_and_import("itertest", [pyx_file])

    assert itertest.run([1,2,3]) == [3,2,1]
    assert list(itertest.run2([1,2,3])) == [1,2,3]

def testSimplePyx():
    pyx_file = os.path.join(test_files, "int_container_class.pyx")

    ics = autowrap.Utils.compile_and_import("ics", [pyx_file], [test_files])
    assert (ics.Xint(3) + ics.Xint(4)).getValue() == 7

    container = ics.XContainerInt()
    assert container.size() ==  0
    container.push_back(ics.Xint(0))
    assert container.size() ==  1
