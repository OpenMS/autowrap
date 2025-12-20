from __future__ import annotations
from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union

from enum import IntEnum as _PyEnum




class NumpyVectorTest:
    """
    Cython implementation of _NumpyVectorTest
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void NumpyVectorTest()
        """
        ...
    
    def sumVector(self, data: numpy.ndarray ) -> float:
        """
        Cython signature: double sumVector(libcpp_vector[double] data)
        """
        ...
    
    def createVector(self, size: int ) -> numpy.ndarray:
        """
        Cython signature: libcpp_vector[double] createVector(size_t size)
        """
        ...
    
    def multiplyVector(self, data: numpy.ndarray , factor: float ) -> None:
        """
        Cython signature: void multiplyVector(libcpp_vector[double] & data, double factor)
        """
        ...
    
    def sumIntVector(self, data: numpy.ndarray ) -> int:
        """
        Cython signature: int sumIntVector(libcpp_vector[int] data)
        """
        ...
    
    def createFloatVector(self, size: int ) -> numpy.ndarray:
        """
        Cython signature: libcpp_vector[float] createFloatVector(size_t size)
        """
        ...
    
    def create2DVector(self, rows: int , cols: int ) -> numpy.ndarray:
        """
        Cython signature: libcpp_vector[libcpp_vector[double]] create2DVector(size_t rows, size_t cols)
        """
        ...
    
    def sum2DVector(self, data: numpy.ndarray ) -> float:
        """
        Cython signature: double sum2DVector(libcpp_vector[libcpp_vector[double]] data)
        """
        ... 

