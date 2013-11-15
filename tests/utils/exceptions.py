#!/usr/bin/python

def ensure_except(exception_type,func,*args,**kwargs):
    try:
        func(*args,**kwargs)
        assert False
    except exception_type as e:
        return e
    else: assert False
