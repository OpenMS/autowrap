#include <vector>
#include <string>
#include <utility>
#include <map>
#include <boost/shared_ptr.hpp>


enum EEE {
    A, B
};


class Int {
    public:
        int i_;
        Int(int i): i_(i) { };
        Int(const Int & i): i_(i.i_) { };
};

class AbstractBaseClass {
    protected:
        AbstractBaseClass(int i): i_(i) {};
    public:
        int i_;
        virtual ~AbstractBaseClass() {};
        virtual int get() = 0;
};

class ABS_Impl1 : public AbstractBaseClass {
    public:
        ~ABS_Impl1() {}
        ABS_Impl1(int i) : AbstractBaseClass(i) {}
        int get() {return i_;}
};

class ABS_Impl2 : public AbstractBaseClass {
    public:
        ~ABS_Impl2() {}
        ABS_Impl2(int i) : AbstractBaseClass(i) {}
        int get() {return i_;}
};


class LibCppTest {

    private:
        int i;

    public:
        LibCppTest(): 
            i(0),
            integer_ptr(0),
            integer_vector_ptr(0) 
        {};

        LibCppTest(int ii): 
            i(ii),
            integer_ptr(0),
            integer_vector_ptr(0) 
        {}

        LibCppTest(const LibCppTest &o): 
            i(o.i),
            integer_ptr(0),
            integer_vector_ptr(0) 
        {}

        Int * integer_ptr;
        std::vector<Int> * integer_vector_ptr;

        bool operator<(const LibCppTest & other) const
        {
            return this->i < other.i;
        }
        bool operator==(const LibCppTest & other) const
        {
            return this->i == other.i;
        }

        int get() { return i; }

        std::pair<int, std::string> twist(std::pair<std::string, int> in)
        {
            return std::pair<int, std::string>(in.second, in.first);
        };

        std::vector<int> process(std::vector<int> & in)
        {
            in.push_back(42);
            return in;
        };
        std::pair<int, int> process2(std::pair<int, int> & in)
        {
            in.first = 42;
            in.second = 11;
            return in;
        };
        std::pair<LibCppTest, int> process3(std::pair<LibCppTest, int> & in)
        {
            in.second = 42;
            return std::pair<LibCppTest, int>(in.first, in.second);
        };

        std::pair<int, LibCppTest> process4(std::pair<int, LibCppTest> & in)
        {
            in.first = 42;
            return std::pair<int, LibCppTest>(in.first, in.second);
        };
        std::pair<LibCppTest, LibCppTest> process5(std::pair<LibCppTest, LibCppTest> & in)
        {
            in.first = 43;
            return std::pair<LibCppTest, LibCppTest>(in.second, in.first);
        };

        std::vector<std::pair<int, double> > process6(std::vector<std::pair<int, double> >& in) {
            in.push_back(std::pair<int,double>(7, 11.0));
            return std::vector<std::pair<int, double> > (in.rbegin(), in.rend());
        }

        std::pair<int, EEE> process7(std::pair<EEE, int> & in ) {
            return std::pair<int, EEE>(in.second, in.first);
        }

        std::vector<EEE> process8(std::vector<EEE> & in ) {
            return std::vector<EEE>(in.rbegin(), in.rend());
        }


        std::set<int> process9(std::set<int> & in ) {
            in.insert(42);
            return in;
        }

        std::set<EEE> process10(std::set<EEE> & in ) {
            in.insert(A);
            return in;
        }

        std::set<LibCppTest> process11(std::set<LibCppTest> & in ) {
            LibCppTest n(42);
            in.insert(n);
            return in;
        }

        std::map<int,float> process12(int i, float f) 
        {
            std::map<int,float> map;
            map[i] = f;
            return map;
        }

        std::map<EEE, int> process13(EEE e, int i) 
        {
            std::map<EEE,int> map;
            map[e] = i;
            return map;
        }

        std::map<int, EEE> process14(EEE e, int i) 
        {
            std::map<int, EEE> map;
            map[i] = e;
            return map;
        }

        std::map<long int, LibCppTest> process15(int i) 
        {
            std::map<long int, LibCppTest> map;
            map[i] = LibCppTest(i);
            return map;
        }

        float process16(std::map<int, float> in)
        {
            return in[42];

        }
        float process17(std::map<EEE, float> in)
        {
            return in[A];

        }

        int process18(std::map<int, LibCppTest> in)
        {
            return in[23].get();
        }

        void  process19(std::map<int, LibCppTest> & in)
        {
            LibCppTest v(12);
            in[23] = v;
        }

        void  process20(std::map<int, float> & in)
        {
            in[23] = 42.0;
        }

        void  process21(std::map<int, float> & in, std::map<int,int> & arg2)
        {
            in[1] = (float) arg2[42];
        }

        void  process22(std::set<int> & in, std::set<float> & arg2)
        {
            std::set<int>::iterator it = in.begin();
            int x = *it;
            in.erase(it);
            arg2.insert((float)x);
        }

        void  process23(std::vector<int> & in, std::vector<float> & arg2)
        {
            int x = *(in.rbegin());
            in.pop_back();
            arg2.push_back((float)x);
        }


        void  process24(std::pair<int, float> & in, std::pair<int,int> & arg2)
        {
            in.first = arg2.second;
            in.second = (float) arg2.first;
        }

        int process25(std::vector<Int> in)
        {
            int sum = 0;
            for (std::vector<Int>::const_iterator i = in.begin(); i != in.end(); ++i)
                sum += i->i_;
            return sum;
        }


        int process26(std::vector<std::vector<Int> > in)
        {
            int sum = 0;
            for (std::vector<std::vector<Int> >::const_iterator i = in.begin(); i != in.end(); ++i)
                sum += process25(*i);
            return sum;
            
        }

        int process27(std::vector<std::vector<std::vector<Int> > > in)
        {
            int sum = 0;
            for (std::vector<std::vector<std::vector<Int> > >::const_iterator i = in.begin(); i != in.end(); ++i)
                sum += process26(*i);
            return sum;
            
        }
        int process28(std::vector<std::vector<std::vector<std::vector<Int> > > > in)

        {
            int sum = 0;
            for (std::vector<std::vector<std::vector<std::vector<Int> > > >::const_iterator i = in.begin(); i != in.end(); ++i)
                sum += process27(*i);
            return sum;
            
        }
        void process29(std::vector<std::vector<Int> > & in)
        {
            for (std::vector<std::vector<Int> >::iterator i = in.begin(); i != in.end(); ++i)
            {
              i->push_back(42);
            }
        }
        void process30(std::vector<std::vector<std::vector<std::vector<Int> > > > & in)
        {
            for (std::vector<std::vector<std::vector<std::vector<Int> > > >::iterator i = in.begin(); i != in.end(); ++i)
            {
                std::vector<std::vector<Int> > newvec;
                std::vector<Int> newvec_inner;
                Int int_obj = Int(42);

                newvec_inner.push_back(int_obj);
                newvec.push_back(newvec_inner);

                i->push_back(newvec);
            }
        }
        
        int process31(const std::vector<int> & in)
        {
            int sum = 0;
            for (std::vector<int>::const_iterator i = in.begin(); i != in.end(); ++i)
                sum += *i;
            return sum;
        }

        int process32(const std::vector<std::vector<int> > & in)
        {
            int sum = 0;
            for (std::vector<std::vector<int> >::const_iterator i = in.begin(); i != in.end(); ++i)
                sum += process31(*i);
            return sum;
        }

        int process33(boost::shared_ptr<Int> in)
        {
            in->i_++;
            return in->i_;
        }


        boost::shared_ptr<Int> process34(boost::shared_ptr<Int> in)
        {
            in->i_++;
            return in;
        }

        boost::shared_ptr<const Int> process35(boost::shared_ptr<Int> in)
        {
            in->i_++;
            return boost::static_pointer_cast<const Int>(in);
        }
           
        int process36(Int* in)
        {
            in->i_++;
            return in->i_;
        }

        Int* process37(Int* in)
        {
            if (in->i_ == 18) return NULL;
            in->i_++;
            return in;
        }

        std::vector<std::vector<unsigned int> > process38(int x) 
        {
            std::vector<std::vector<unsigned int> > res;
            std::vector<unsigned int> res_inner;
            res_inner.push_back(x);
            res.push_back(res_inner);
            res.push_back(res_inner);
            return res;
        }

        const Int* process39(Int* in)
        {
            in->i_++;
            return in;
        }

        int process40(AbstractBaseClass* in)
        {
            return in->get();
        }
};
