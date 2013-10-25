#!/usr/bin/python

class Enum(object):
    def __init__(self, *seq, **named):
	enums = dict([(seq[i],i) for i in range(len(seq))], **named)
        self.__dict__.update(enums)
