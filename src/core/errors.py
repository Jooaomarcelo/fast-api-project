class AppError(Exception):
    """Base class for API exceptions."""

    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        self.message = message
        self.status_code = status_code
        self.status = "fail" if 400 <= status_code < 500 else "error"
        self.is_operational = True
        super().__init__(self.message)
