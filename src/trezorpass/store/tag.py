class Tag:
    def __init__(self, title: str) -> None:
        self.title = title

    @staticmethod
    def load(dict):
        tag = Tag(dict["title"])
        return tag

    def __str__(self) -> str:
        return self.title