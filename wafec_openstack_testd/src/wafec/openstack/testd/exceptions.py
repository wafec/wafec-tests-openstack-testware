import abc


class ExceptionBase(Exception, metaclass=abc.ABCMeta):
    pass


class NotFoundException(ExceptionBase):
    pass


class StateMismatchException(ExceptionBase):
    pass
