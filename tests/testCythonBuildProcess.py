import os

def testBuildExt():
    test_files = os.path.join(os.path.dirname(__file__), 'test_files')
    os.chdir(test_files)
    try:
        os.remove("itertest.cpp")
    except:
        pass
    stat = os.system("python setup_itertest.py build_ext --inplace")
    assert stat == 0
    import sys
    sys.path.insert(0, ".")
    import itertest
    assert itertest.run([1,2,3]) == [3,2,1]
    assert list(itertest.run2([1,2,3])) == [1,2,3]
