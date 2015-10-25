class Singleton(type):
    """
    A metaclass for making classes Singletons.

    Example usage:

    >>> class A(object):
    >>>     __metaclass__ = Singleton
    >>>     def __init__(self, a, b):
    >>>         self.a = a
    >>>         self.b = b
    >>> x = A(1,2)
    >>> repr(x)
    <A object at 0x7fe6a76d8510>
    >>> y = A(1,2)
    >>> repr(y)
    '<A object at 0x7fe6a76d8510>'

    However, note that Singletons ignore the arguments that they are given for
    subsequent constructions. That means that we can have a somewhat
    unexpected result when trying to get another instance of A:

    >>> z = A('abc', 'def')
    >>> repr(z)
    '<A object at 0x7fe6a76d8510>'
    """
    def __call__(cls, *args, **kwargs):
        """
        Redefine class construction to start by looking for an instance of the
        class to return and returning it if found
        """
        # try to pull a class instance out of the class
        try:
            instance = cls._instance
        # if we get an AttributeError, that means that `cls._instance` was
        # never set, so we need to set it, and return it
        except AttributeError:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
            instance = cls._instance

        return instance
