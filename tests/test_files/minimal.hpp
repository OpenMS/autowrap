#include <string>
#include <vector>

typedef int Int;

enum ABCorD {
        A, B=2, C, D
};


class Minimal {

    private:
        int _i;
        std::vector<Minimal> _mi;

    public:

        static const int m_const = -1;
        static const int m_constdef = -1;
        int m_accessible;
        bool m_bool;

        Minimal();
        Minimal(Int);
        Minimal(std::vector<int> const &);
        Minimal(const Minimal &);

        int get() { return _i; }

        int compute(Int i) const;
        float compute(float i) const;
        Int compute(int, int) const;
        std::string compute(std::string s) const;

        char *pass_charptr(char *) const;
        const char *pass_const_charptr(const char *) const;

        int compute_int(int i) const;
        int compute_int() const;
        std::string compute_str(std::string s) const;
        int compute_charp(char *p) const;
        int run(const Minimal &) const;
        int run2(Minimal *) const;
        int run3(Minimal &) const;
        int run4(Minimal &) const;

        unsigned int test_special_converter(unsigned int l) const;

        int sumup(const std::vector<int> &) const;
        int call(std::vector<Minimal> & arg) const;
        int call2(std::vector<Minimal> & arg) const;
        int call3(std::vector<Minimal> & arg) const;
        int call4(int & arg) const;
        int call_str(std::vector<std::string> & arg) const;

        bool operator==(const Minimal &other) const;

        int size() const {
            return _mi.size();
        }

        int operator[](const int i) const
        {
            return i+1;
        };

        std::vector<std::string> message() const;
        std::vector<Minimal> create_two() const;

        void setVector(std::vector<Minimal> in);
        std::vector<Minimal> getVector() const;

        int test2Lists(const std::vector<Minimal> &, const std::vector<int> &) const;

        std::vector<Minimal>::iterator begin();
        std::vector<Minimal>::iterator end();

        std::vector<Minimal>::reverse_iterator rbegin();
        std::vector<Minimal>::reverse_iterator rend();

        Minimal create() const;

        Minimal & getRef();

        enum ABCorD enumTest(enum ABCorD) const;

        static long int run_static(long int, bool = true);

        operator int() const {
            return 4711;
        }

        Minimal operator+(Minimal that)
        {
            return Minimal(this->_i + that._i);
        }
        Minimal operator-(Minimal that)
        {
            return Minimal(this->_i - that._i);
        }
        Minimal operator+=(Minimal that)
        {
            this->_i = this->_i + that._i;
            return *this;
        }
        Minimal operator*(Minimal that)
        {
            return Minimal(this->_i * that._i);
        }
        Minimal operator/(Minimal that)
        {
            return Minimal(this->_i / that._i);
        }
        Minimal operator%(Minimal that)
        {
            return Minimal(this->_i % that._i);
        }
        Minimal operator<<(Minimal that)
        {
            return Minimal(this->_i << that._i);
        }
        Minimal operator>>(Minimal that)
        {
            return Minimal(this->_i >> that._i);
        }
        Minimal operator*=(Minimal that)
        {
            this->_i = this->_i * that._i;
            return *this;
        }
        Minimal operator-=(Minimal that)
        {
            this->_i = this->_i - that._i;
            return *this;
        }
        Minimal operator/=(Minimal that)
        {
            this->_i = this->_i / that._i;
            return *this;
        }
        Minimal operator%=(Minimal that)
        {
            this->_i = this->_i % that._i;
            return *this;
        }
        Minimal operator<<=(Minimal that)
        {
            this->_i = this->_i << that._i;
            return *this;
        }
        Minimal operator>>=(Minimal that)
        {
            this->_i = this->_i >> that._i;
            return *this;
        }
        Minimal operator&(Minimal that)
        {
            return Minimal(this->_i & that._i);
        }
        Minimal operator|(Minimal that)
        {
            return Minimal(this->_i | that._i);
        }
        Minimal operator^(Minimal that)
        {
            return Minimal(this->_i ^ that._i);
        }
        Minimal operator&=(Minimal that)
        {
            this->_i = this->_i & that._i;
            return *this;
        }
        Minimal operator|=(Minimal that)
        {
            this->_i = this->_i | that._i;
            return *this;
        }
        Minimal operator^=(Minimal that)
        {
            this->_i = this->_i ^ that._i;
            return *this;
        }

};

int top_function(int i);
int sumup(std::vector<int> &);

