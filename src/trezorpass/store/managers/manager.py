class Manager:
    @property
    def password_store(self) -> bytes:
        raise NotImplementedError()