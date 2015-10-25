def assert_substr(full, sub):
    assert sub in full, "{0}\ndoesn't contain\n{1}".format(full, sub)


def ensure_except(exception_type, func, *args, **kwargs):
    """
    Ensures that a function raises the desired exception.
    Asserts False (and therefore fails) when it does not.
    """
    try:
        func(*args, **kwargs)
        # fail if the function call succeeds
        assert False
    # return the desired exception, in case it needs to be
    # inspected by the calling context
    except exception_type as e:
        return e
    # fail if the wrong exception is raised
    else:
        assert False


def ensure_SystemExit_with_code(code, func, *args, **kwargs):
    """
    Ensures that a function raises a SystemExit with the given code.
    """
    e = ensure_except(SystemExit, func, *args, **kwargs)
    assert e.code == code


def disambiguate_by_class(klass, obj1, obj2):
    """
    Take two objects and a class, and return them in a tuple such that the
    first element matches the given class. Doesn't check the second object.

    Args:
        @klass
        The class to match against.

        @obj1, @obj2
        Objects to inspect, unordered
    """
    if isinstance(obj1, klass):
        return obj1, obj2
    else:
        return obj2, obj1
