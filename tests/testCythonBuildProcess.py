import os

def testBuildExt():
    assert os.environ.get("VIRTUAL_ENV") != None, "PLEASE RUN THIS TEST IN"\
                                                  "VIRTUAL ENV !!!"
    test_files = os.path.join(os.path.dirname(__file__), 'test_files')
    os.chdir(test_files)
    stat = os.system("python setup_itertest.py develop")
    assert stat == 0
    import itertest
    print itertest.__file__
    assert itertest.run([1,2,3]) == [3,2,1]
    assert list(itertest.run2([1,2,3])) == [1,2,3]

def testSimplePyx():
    assert os.environ.get("VIRTUAL_ENV") != None, "PLEASE RUN THIS TEST IN"\
                                                  "VIRTUAL ENV !!!"
    test_files = os.path.join(os.path.dirname(__file__), 'test_files')
    os.chdir(test_files)
    stat = os.system("python setup_int_container_class.py develop")
    assert stat == 0
    import int_container_class as ics
    print ics.__file__
    assert (ics.Xint(3) + ics.Xint(4)).getValue() == 7

    container = ics.XContainerInt()
    assert container.size() ==  0
    container.push_back(ics.Xint(0))
    assert container.size() ==  1
