
inline char * _cast_const_away(const char *p)
{
    return const_cast<char *>(p);
}

template<class A> void _iadd(A * a1, const A * a2)
{
    (*a1) += (*a2);
}
