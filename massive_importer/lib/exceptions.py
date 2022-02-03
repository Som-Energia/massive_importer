# -*- coding: utf-8 -*-

class MassiveImporterException(Exception):

    def __init__(self, msg):
        super(MassiveImporterException, self).__init__(msg)
        self.msg = msg

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.__repr__()


class InvalidEncodingException(MassiveImporterException):

    def __init__(self, msg):
        super(InvalidEncodingException, self).__init__(msg)
        self.msg = msg

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.__repr__()

class EventToImportFileException(MassiveImporterException):

    def __init__(self, msg):
        super(EventToImportFileException, self).__init__(msg)
        self.msg = msg

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.__repr__()

class TooFewArgumentsException(MassiveImporterException):

    def __init__(self, msg):
        super(TooFewArgumentsException, self).__init__(msg)
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

class CrawlingProcessException(Exception):
    def __init__(self, msg, download_was_clicked=False):
        dwc_msg = "[S'ha fet click a descarregar: {}]".format(download_was_clicked)
        self.msg = '\n'.join([msg,dwc_msg])

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.msg

class CrawlingLoginException(CrawlingProcessException):
    def __init__(self, msg, download_was_clicked=False):
        super(CrawlingLoginException, self).__init__(msg, download_was_clicked)

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.msg

class CrawlingFilteringException(CrawlingProcessException):
    def __init__(self, msg, download_was_clicked=False):
        super(CrawlingFilteringException, self).__init__(msg, download_was_clicked)

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.msg

class CrawlingDownloadingException(CrawlingProcessException):
    def __init__(self, msg, download_was_clicked=False):
        super(CrawlingDownloadingException, self).__init__(msg, download_was_clicked)

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.msg

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