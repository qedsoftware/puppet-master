
class PuppetMasterException(Exception):
    pass


class SeleniumAssertionError(PuppetMasterException, AssertionError):
    pass


class MissingDataException(PuppetMasterException):
    pass
