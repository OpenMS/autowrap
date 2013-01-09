#include <string>
#include <vector>

enum ABCorD {
        A, B=2, C, D
};


class Minimal {

    private:
        int _i;
        std::vector<Minimal> _mi;

    public:

        Minimal();
        Minimal(int);
        Minimal(std::vector<int> const &);
        Minimal(const Minimal &);

        int compute(int i) const;
        int compute(int, int) const;
        std::string compute(std::string s) const;

        const char *pass_charptr(const char *) const;

        int compute_int(int i) const;
        int compute_int() const;
        std::string compute_str(std::string s) const;
        int compute_charp(char *p) const;
        int run(const Minimal &) const;
        int run2(Minimal *) const;

        int sumup(std::vector<int> &) const;
        int call(std::vector<Minimal> & arg) const;
        int call2(std::vector<std::string> & arg) const;

        bool operator==(const Minimal &other) const;

        std::vector<std::string> message() const;
        std::vector<Minimal> create_two() const;

        void setVector(std::vector<Minimal> in);
        std::vector<Minimal> getVector() const;

        std::vector<Minimal>::iterator begin();
        std::vector<Minimal>::iterator end();

        Minimal create() const;

        Minimal & getRef();

        enum ABCorD enumTest(enum ABCorD) const;
};
