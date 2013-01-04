#include <string>
#include <vector>

class Minimal {

    private:
        int _i;

    public:

        Minimal();
        Minimal(int);
        Minimal(std::vector<int> const &);
        Minimal(const Minimal &);

        int compute(int i) const;
        int compute(int, int) const;
        std::string compute(std::string s) const;
        int compute_int(int i) const;
        int compute_int() const;
        std::string compute_str(std::string s) const;
        int compute_charp(char *p) const;
        int run(const Minimal &) const;
        int run2(Minimal *) const;

        int sumup(std::vector<int> &) const;
        int call(std::vector<Minimal> & arg) const;
        int call2(std::vector<std::string> & arg) const;

        Minimal create() const;
};
