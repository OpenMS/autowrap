# cython: language_level=3
from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector
from libcpp cimport bool

cdef extern from "wrap_len_test.hpp":

    # Basic container with wrap-len using size()
    cdef cppclass BasicContainer:
        # wrap-len:
        #   size()

        BasicContainer()
        BasicContainer(int count)

        size_t size()
        void add(int value)
        void clear()
        int get(size_t index)

    # Container with length() method - wrap-len using length()
    cdef cppclass LengthContainer:
        # wrap-len:
        #   length()

        LengthContainer()

        int length()
        void append(libcpp_string item)
        libcpp_string getItem(int index)

    # Container with count() method
    cdef cppclass CountContainer:
        # wrap-len:
        #   count()

        CountContainer()
        CountContainer(int initial)

        unsigned int count()
        void increment()
        void decrement()

    # Container with size() but NO wrap-len annotation
    # This should NOT have __len__ in Python
    cdef cppclass NoLenContainer:
        NoLenContainer()

        size_t size()
        void push(double v)
        double sum()

    # Container where size() is wrap-ignored
    # wrap-len should still work since it directly calls C++ method
    cdef cppclass IgnoredSizeContainer:
        # wrap-len:
        #   size()

        IgnoredSizeContainer()
        IgnoredSizeContainer(int count)

        size_t size()  # wrap-ignore
        void add(int v)
        int get(size_t i)

    # Container using getSize() method name
    cdef cppclass GetSizeContainer:
        # wrap-len:
        #   getSize()

        GetSizeContainer()
        GetSizeContainer(int s)

        size_t getSize()
        void setSize(int s)

    # Empty container that always returns 0
    cdef cppclass EmptyContainer:
        # wrap-len:
        #   size()

        EmptyContainer()
        size_t size()

    # Template container - test wrap-len with templates
    cdef cppclass TemplateContainer[T]:
        # wrap-instances:
        #   IntTemplateContainer := TemplateContainer[int]
        #   StringTemplateContainer := TemplateContainer[libcpp_string]
        # wrap-len:
        #   size()

        TemplateContainer()

        size_t size()
        void add(T value)
        T get(size_t index)

    # Container with both size() and length() - test that wrap-len picks correctly
    # Here we choose length() which returns size * 2
    cdef cppclass DualLenContainer:
        # wrap-len:
        #   length()

        DualLenContainer()
        DualLenContainer(int count)

        size_t size()
        size_t length()
        void add(int v)
