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
            {
                (*in.begin())->i_ += 10;
                return (*in.begin())->i_;
            }

            return -1;
        }

        std::set<IntWrapper*> process_2_set(IntWrapper* in)
        {
            std::set<IntWrapper*> res;
            res.insert(in);
            return res;
        }

        int process_3_vector(std::vector< boost::shared_ptr<IntWrapper> > & in)
        {
            boost::shared_ptr<IntWrapper> ptr(new IntWrapper(42));
            in.push_back(ptr);

            if (!in.empty() )
            {
                (*in.begin())->i_ += 10;
                return (*in.begin())->i_;
            }

            return -1;
        }

        std::vector< boost::shared_ptr<IntWrapper> > process_4_vector(boost::shared_ptr<IntWrapper> & in)
        {
            in->i_ += 10;
            std::vector< boost::shared_ptr<IntWrapper> > res;
            res.push_back(in);
            return res;
        }
};
