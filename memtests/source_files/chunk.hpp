#include<iostream>
#include<vector>

class Chunk {

    private:
        int * memory;
        bool debug;


    public:

    Chunk(): debug(0) { 

        memory = new int[1024*1024];  // 1 MB
    }


    Chunk(bool _debug): debug(_debug) {
        if (debug)
            std::cout << "allocate" << std::endl;
        memory = new int[1024*1024];  // 1 MB
        if (debug)
            std::cout << "allocated" << std::endl;

    }

    Chunk(const Chunk &other)
    {
        debug = other.debug;
        if (debug)
            std::cout << "copy cons" << std::endl;
        memory = new int[1024*1024];  // 1 MB
        if (debug)
            std::cout << "copy cons done" << std::endl;

    }

    ~Chunk()
    {
        if (debug)
            std::cout << "deallocate" << std::endl;
        delete[] memory;
        if (debug)
            std::cout << "deallocated" << std::endl;
    }

    Chunk & operator=(const Chunk & other)
    {
        if (debug) std::cout << "operator=" << std::endl;
        if (&other == this)
        {
            if (debug) std::cout << "operator= on same obj" << std::endl;
            return *this;
        }
        delete[] memory;
        memory = new int[1024*1024];  // 1 MB
        if (debug) std::cout << "operator= done" << std::endl;
        debug = other.debug;
        return *this;
    }

    Chunk & getRef()
    {
        return *this;
    }

    Chunk getCopy()
    {
        return *this;
    }

    std::vector<Chunk> create(int n)
    {
        std::vector<Chunk> rv;
        for (int i=0; i<n; ++i)
        {
            Chunk c(*this);
            rv.push_back(c);
        }
        return rv;
    }

    std::vector<Chunk> copy(std::vector<Chunk> in)
    {
        return in;
    }

};
