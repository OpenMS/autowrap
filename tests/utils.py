def expect_exception(fun):
    def wrapper(*a, **kw):
        try:
            fun(*a, **kw)
        except Exception:
            if 0:
                print "info: expected excption. here some more info:"
                import traceback
                traceback.print_exc()
                print
            pass
        else:
            assert False, "%s did not raise exception" % fun
    # set name, so that test frame work recognizes wrapped function
    wrapper.__name__ = fun.__name__+"__exception_wrapped"
    return wrapper
