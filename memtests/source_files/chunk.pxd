from libcpp.vector cimport vector as std_vector

cdef extern  from "chunk.hpp":

    cdef cppclass Chunk:
        #Chunk()  # no-wrap
        Chunk(int debug)
        Chunk(Chunk &)

        # Chunk& operator=(Chunk other &) # wrap-ignore

        Chunk & getRef()
        Chunk getCopy()

        std_vector[Chunk] create(int n)
        std_vector[Chunk] copy(std_vector[Chunk])

