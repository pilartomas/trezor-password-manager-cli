from dataclasses import dataclass


@dataclass(kw_only=True)
class Tag:
    title: str
