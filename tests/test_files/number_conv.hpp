#include <vector>
#include <float.h>

double add_max_float(double d)
{
    return d + FLT_MAX;
}

double pass_full_precision(double v)
{
    return v + 0.0;
}

std::vector<double> pass_full_precision_vec(std::vector<double> & in)
{
    for (std::vector<double>::iterator it = in.begin(); it != in.end(); ++it)
        *it = *it + 0.0;
    return in;
}


