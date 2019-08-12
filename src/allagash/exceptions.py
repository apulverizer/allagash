

class NotSolvedException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InfeasibleException(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnboundedException(Exception):
    def __init__(self, message):
        super().__init__(message)


class UndefinedException(Exception):
    def __init__(self, message):
        super().__init__(message)