#include <string>

class Minimal {

    private:
        int _i;

    public:

        Minimal();
        Minimal(int);
        Minimal(const Minimal &);

        int compute(int i) const;
        std::string compute(std::string s) const;
        int compute_int(int i) const;
        std::string compute_str(std::string s) const;
        int compute_charp(char *p) const;
        int run(const Minimal &) const;
        int run2(Minimal *) const;

        Minimal create() const;
};
