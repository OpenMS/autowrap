from libcpp.vector cimport vector as libcpp_vector

cdef extern from "numpy_vector_test.hpp":
    cdef cppclass NumpyVectorTest:
        NumpyVectorTest()
        
        # Test simple vector input
        double sumVector(libcpp_vector[double] data)
        
        # Test simple vector output
        libcpp_vector[double] createVector(size_t size)
        
        # Test simple vector input/output (modify in place via reference)
        void multiplyVector(libcpp_vector[double]& data, double factor)
        
        # Test different numeric types
        int sumIntVector(libcpp_vector[int] data)
        libcpp_vector[float] createFloatVector(size_t size)
        
        # Test nested vectors (2D arrays)
        libcpp_vector[libcpp_vector[double]] create2DVector(size_t rows, size_t cols)
        double sum2DVector(libcpp_vector[libcpp_vector[double]] data)
