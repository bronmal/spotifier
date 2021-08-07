from enum import Enum
from dataclasses import dataclass


class Browser(Enum):
    Firefox = 1
    Chrome = 2
    Edge = 3


@dataclass(frozen=True)
class Account:
    login: str
    password: str

