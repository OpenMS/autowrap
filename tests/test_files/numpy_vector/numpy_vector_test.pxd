from libcpp.vector cimport vector as libcpp_vector_as_np

cdef extern from "numpy_vector_test.hpp":
    cdef cppclass NumpyVectorTest:
        NumpyVectorTest()
        
        # Test vector outputs with different qualifiers
        const libcpp_vector_as_np[double]& getConstRefVector()  # const ref -> copy
        libcpp_vector_as_np[double]& getMutableRefVector()  # non-const ref -> view
        libcpp_vector_as_np[double] getValueVector(size_t size)  # value -> copy
        
        # Test simple vector input
        double sumVector(libcpp_vector_as_np[double] data)
        
        # Test different numeric types
        int sumIntVector(libcpp_vector_as_np[int] data)
        libcpp_vector_as_np[float] createFloatVector(size_t size)
        
        # Test nested vectors (2D arrays)
        libcpp_vector_as_np[libcpp_vector_as_np[double]] create2DVector(size_t rows, size_t cols)
        double sum2DVector(libcpp_vector_as_np[libcpp_vector_as_np[double]] data)
