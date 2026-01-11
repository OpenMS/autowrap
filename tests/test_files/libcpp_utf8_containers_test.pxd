# cython: language_level=3
from libcpp.string cimport string as libcpp_utf8_output_string
from libcpp.string cimport string as libcpp_utf8_string
from libcpp.string cimport string as libcpp_string
from libcpp.vector cimport vector as libcpp_vector
from libcpp.set cimport set as libcpp_set
from libcpp.map cimport map as libcpp_map
from libcpp.unordered_set cimport unordered_set as libcpp_unordered_set
from libcpp.unordered_map cimport unordered_map as libcpp_unordered_map

cdef extern from "libcpp_utf8_containers_test.hpp":
    cdef cppclass Utf8ContainersTest:
        Utf8ContainersTest()

        # Vector - output decoded to str, input accepts str/bytes
        libcpp_vector[libcpp_utf8_output_string] get_vector()
        libcpp_vector[libcpp_utf8_output_string] echo_vector(
            libcpp_vector[libcpp_utf8_string]
        )

        # Set - output decoded to str, input accepts str/bytes
        libcpp_set[libcpp_utf8_output_string] get_set()
        libcpp_set[libcpp_utf8_output_string] echo_set(
            libcpp_set[libcpp_utf8_string]
        )

        # Map - both keys and values as UTF-8
        libcpp_map[libcpp_string, libcpp_utf8_output_string] get_map()
        libcpp_map[libcpp_string, libcpp_utf8_output_string] echo_map(
            libcpp_map[libcpp_string, libcpp_utf8_string]
        )

        # Map with UTF-8 keys
        libcpp_map[libcpp_utf8_output_string, int] get_map_utf8_keys()

        # Unordered set
        libcpp_unordered_set[libcpp_utf8_output_string] get_unordered_set()
        libcpp_unordered_set[libcpp_utf8_output_string] echo_unordered_set(
            libcpp_unordered_set[libcpp_utf8_string]
        )

        # Unordered map - both keys and values as UTF-8
        libcpp_unordered_map[libcpp_utf8_output_string, libcpp_utf8_output_string] get_unordered_map()
        libcpp_unordered_map[libcpp_utf8_output_string, libcpp_utf8_output_string] echo_unordered_map(
            libcpp_unordered_map[libcpp_utf8_string, libcpp_utf8_string]
        )
