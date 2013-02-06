#include <vector>
#include <string>
#include <utility>


class LibCppTest {
    private:
        int i;
    public:
        LibCppTest(): i(0) { };
        LibCppTest(int ii): i(ii) { };

        LibCppTest(const LibCppTest &o): i(o.i)  {
        };

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
};
