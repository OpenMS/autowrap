
inline char * _cast_const_away(const char *p)
{
    return const_cast<char *>(p);
}

template<class A> void _iadd(A * a1, const A * a2)
{
    (*a1) += (*a2);
}

namespace autowrap {

    template <class X>
    class AutowrapRefHolder {

        private:

            X& _ref;

        public:

            AutowrapRefHolder(X &ref): _ref(ref) 
            {
            }

            X& get()
            {
                return _ref;
            }

            void assign(const X & refneu)
            {
                _ref = refneu;
            }
    };

    template <class X>
    class AutowrapPtrHolder {

        private:

            X* _ptr;

        public:

            AutowrapPtrHolder() {}

            AutowrapPtrHolder(X *ref): _ptr(ref) 
            {
            }

            X* get()
            {
                return _ptr;
            }

            void assign(X * ptr)
            {
                _ptr = ptr;
            }
    };

    template <class X>
    class AutowrapConstPtrHolder {

        private:

            const X* _ptr;

        public:

            AutowrapConstPtrHolder() {}

            AutowrapConstPtrHolder(const X *ref): _ptr(ref) 
            {
            }

            const X* get()
            {
                return _ptr;
            }

            void assign(const X * ptr)
            {
                _ptr = ptr;
            }
    };

};
