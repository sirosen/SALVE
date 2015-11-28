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


def first_param_docfunc(func, num, params):
    """
    A generic docfunc for usage with nose_parameterized
    Takes the first argument given to the function and uses it as the
    description, without doing any logic. Lets a raw docstring get inserted
    into the parameter list. As an unfortunate side-effect it must then be
    passed to the test function itself.

    Args:
        @func
        The test function itself.

        @num
        The index of @params in the list of parameters.

        @params
        A pair (args, kwargs) which will be passed to @func
        We really just care about the args[0] value here, since that's the
        first value in the arg list.
    """
    (args, kwargs) = params
    return args[0]
