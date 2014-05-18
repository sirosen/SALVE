#!/usr/bin/python


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
