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
    
    def getConstRefVector(self) -> numpy.ndarray:
        """
        Cython signature: const libcpp_vector_as_np[double] & getConstRefVector()
        """
        ...
    
    def getMutableRefVector(self) -> numpy.ndarray:
        """
        Cython signature: libcpp_vector_as_np[double] & getMutableRefVector()
        """
        ...
    
    def getValueVector(self, size: int ) -> numpy.ndarray:
        """
        Cython signature: libcpp_vector_as_np[double] getValueVector(size_t size)
        """
        ...
    
    def sumVector(self, data: numpy.ndarray ) -> float:
        """
        Cython signature: double sumVector(libcpp_vector_as_np[double] data)
        """
        ...
    
    def sumIntVector(self, data: numpy.ndarray ) -> int:
        """
        Cython signature: int sumIntVector(libcpp_vector_as_np[int] data)
        """
        ...
    
    def createFloatVector(self, size: int ) -> numpy.ndarray:
        """
        Cython signature: libcpp_vector_as_np[float] createFloatVector(size_t size)
        """
        ...
    
    def create2DVector(self, rows: int , cols: int ) -> numpy.ndarray:
        """
        Cython signature: libcpp_vector_as_np[libcpp_vector_as_np[double]] create2DVector(size_t rows, size_t cols)
        """
        ...
    
    def sum2DVector(self, data: numpy.ndarray ) -> float:
        """
        Cython signature: double sum2DVector(libcpp_vector_as_np[libcpp_vector_as_np[double]] data)
        """
        ... 

