from _typeshed import Incomplete
from pygments.style import Style
from typing import Type

class DefaultJsonStyle(Style):
    styles: Incomplete

def pretty_json(data: dict, indent: int = ..., colored: bool = ..., style: Type[Style] = ...) -> str: ...

data: Incomplete

def main() -> None: ...
