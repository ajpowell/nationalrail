class NoFileSpecified(RuntimeError):
    def __init__(self):
        super().__init__()
        self.message = "NoFileSpecified"


class InvalidConfigError(Exception):
    def __init__(self, message: str):
        super().__init__()
        self.message = f"InvalidConfigError:  {message}"
