#!/usr/bin/python

class StreamContext(object):
    def __init__(self,filename,lineno):
        self.filename = filename
        self.lineno = lineno

    def __str__(self):
        return str(self.filename) + ': ' + str(self.lineno)


class SALVEException(StandardError):
    def __init__(self,message,context):
        StandardError.__init__(self,message)
        self.message = message
        self.context = context
