#include <vector>
#include <string>
#include <utility>
#include <map>
#include <boost/shared_ptr.hpp>

class IntWrapper {
    public:
        int i_;
        IntWrapper(int i): i_(i) { };
};

class LibCppSTLTest {

    public:
        LibCppSTLTest() {};

        int process_1_set(std::set<IntWrapper*> & in)
        {
            if (!in.empty() )
                (*in.begin())->i_ += 10;
                return (*in.begin())->i_;

            return -1;
        }
        std::set<IntWrapper*> process_2_set(IntWrapper* in)
        {
            std::set<IntWrapper*> res;
            res.insert(in);
            return res;
        }
};
