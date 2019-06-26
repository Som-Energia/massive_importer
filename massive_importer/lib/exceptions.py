# -*- coding: utf-8 -*-

class MassiveImporterException(Exception):

    def __init__(self, msg):
        super(MassiveImporterException, self).__init__(msg)
        self.msg = msg

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.__repr__()

class ImproperlyConfigured(MassiveImporterException):

    def __init__(self, msg):
        super(ImproperlyConfigured, self).__init__(msg)
        self.msg = msg

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.__repr__()

class CrawlingProcessException(MassiveImporterException):
    def __init__(self, msg):
        super(CrawlingProcessException, self).__init__(msg)
        self.msg = msg
    
    def __repr__(self):
        return self.msg
    
    def __str__(self):
        return super().__repr__()

class FileToBucketException(MassiveImporterException):
    def __init__(self, msg):
        super(FileToBucketException, self).__init__(msg)
        self.msg = msg
    
    def __repr__(self):
        return self.msg
    
    def __str__(self):
        return super().__repr__()

class ModuleImportingException(MassiveImporterException):
    def __init__(self, msg):
        super(FileToBucketException, self).__init__(msg)
        self.msg = msg
    
    def __repr__(self):
        return self.msg
    
    def __str__(self):
        return super().__repr__()