#include <vector>

class VecHolder
{
public:
    std::vector<float> data_;
    VecHolder() : data_(){};
    VecHolder(std::vector<float> data) : data_(data){};

    float &get(size_t i)
    {
        return data_[i];
    }

    float &operator[](size_t i)
    {
        return data_[i];
    }

    size_t add(float value)
    {
        data_.push_back(value);
        return size();
    }

    size_t size() { return data_.size(); }

    std::vector<float>::iterator begin() { return data_.begin(); }
    std::vector<float>::iterator end() { return data_.end(); }
};