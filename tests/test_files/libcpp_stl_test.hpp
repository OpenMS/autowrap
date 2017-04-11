#include <vector>
#include <string>
#include <utility>
#include <map>
#include <boost/shared_ptr.hpp>

class IntWrapper {

    public:
        int i_;

        IntWrapper(): 
          i_(0) 
        {}

        IntWrapper(const int i): 
          i_(i) 
        {}

        // for map
        bool operator<( const IntWrapper & other ) const 
        {
          return this->i_ < other.i_;
        }
};

class MapWrapper {

    public:
      std::map<int, double> map_;

      MapWrapper() {}
      MapWrapper(const MapWrapper& other) 
      {
        map_ = other.map_;
      }
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

        int process_5_vector(std::vector<IntWrapper*> & in)
        {
            if (!in.empty() )
            {
                (*in.begin())->i_ += 10;
                return (*in.begin())->i_;
            }

            return -1;
        }

        std::vector<IntWrapper*> process_6_vector(IntWrapper* in)
        {
            std::vector<IntWrapper*> res;
            res.push_back(in);
            return res;
        }

        int process_7_map(std::map<IntWrapper, int>& in)
        {
            if (!in.empty() )
            {
                in.begin()->second += 10;
                return in.begin()->first.i_;
            }
            return -1;
        }

        std::map<IntWrapper, int> process_8_map(int in_)
        {
            std::map<IntWrapper, int> res;
            IntWrapper wr(in_);
            res[wr] = in_ + 10;
            return res;
        }

        int process_9_map(std::map<int, IntWrapper>& in)
        {
            if (!in.empty() )
            {
                in.begin()->second.i_ += 10;
                return in.begin()->first;
            }
            return -1;
        }

        std::map<int, IntWrapper> process_10_map(int in_)
        {
            std::map<int, IntWrapper> res;
            IntWrapper wr(in_);
            res[in_ + 10] = wr;
            return res;
        }

        boost::shared_ptr<const IntWrapper> process_11_const()
        {
            boost::shared_ptr<IntWrapper> ptr(new IntWrapper(42));
            return boost::static_pointer_cast<const IntWrapper>(ptr);
        }
};
