
########################################################################
########################################################################
########################################################################
## Python 3 compatibility functions
########################################################################
from cpython.version cimport PY_MAJOR_VERSION, PY_MINOR_VERSION
from cpython cimport PyBytes_Check, PyUnicode_Check
from cpython cimport array as c_array
from libcpp.string  cimport string as libcpp_string

cdef bint IS_PYTHON3 = PY_MAJOR_VERSION >= 3

cdef from_string_and_size(const char* s, size_t length):
    if IS_PYTHON3:
        return s[:length].decode("utf8")
    else:
        return s[:length]


# filename encoding
cdef str FILENAME_ENCODING = sys.getfilesystemencoding() or sys.getdefaultencoding() or 'ascii'
cdef str TEXT_ENCODING = 'utf-8'

cdef bytes encode_filename(object filename):
    """Make sure a filename is 8-bit encoded (or None)."""
    if filename is None:
        return None
    elif PY_MAJOR_VERSION >= 3 and PY_MINOR_VERSION >= 2:
        # Added to support path-like objects
        return os.fsencode(filename)
    elif PyBytes_Check(filename):
        return filename
    elif PyUnicode_Check(filename):
        return filename.encode(FILENAME_ENCODING)
    else:
        raise TypeError("Argument must be string or unicode.")


cdef bytes force_bytes(object s, encoding=TEXT_ENCODING):
    """convert string or unicode object to bytes, assuming
    utf8 encoding.
    """
    if s is None:
        return None
    elif PyBytes_Check(s):
        return s
    elif PyUnicode_Check(s):
        return s.encode(encoding)
    else:
        raise TypeError("Argument must be string, bytes or unicode.")


cdef charptr_to_str(const char* s, encoding=TEXT_ENCODING):
    if s == NULL:
        return None
    if PY_MAJOR_VERSION < 3:
        return s
    else:
        return s.decode(encoding)


cdef charptr_to_str_w_len(const char* s, size_t n, encoding=TEXT_ENCODING):
    if s == NULL:
        return None
    if PY_MAJOR_VERSION < 3:
        return s[:n]
    else:
        return s[:n].decode(encoding)


cdef bytes charptr_to_bytes(const char* s, encoding=TEXT_ENCODING):
    if s == NULL:
        return None
    else:
        return s


cdef force_str(object s, encoding=TEXT_ENCODING):
    """Return s converted to str type of current Python
    (bytes in Py2, unicode in Py3)"""
    if s is None:
        return None
    if PY_MAJOR_VERSION < 3:
        return s
    elif PyBytes_Check(s):
        return s.decode(encoding)
    else:
        # assume unicode
        return s

