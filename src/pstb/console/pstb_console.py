""" 
Module for the console interface of the package. 
Actives the rich traceback if the PYTHON_RICH_TRACEBACK environment variable is set.

Functions:
    pretty_json: Return a pretty formatted JSON string.
    
"""
import json
import os
from typing import Type

from dotenv import load_dotenv
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers import JsonLexer
from pygments.style import Style
from pygments.token import Keyword, Literal, Number, String
from rich.traceback import install

load_dotenv()

# Enable rich traceback if PYTHON_RICH_TRACEBACK is set
if os.getenv("PYTHON_RICH_TRACEBACK"):
    install()


# Define a custom style
class DefaultJsonStyle(Style):
    styles = {
        Number: "ansiblue",  # style for numbers
        String: "ansigreen",  # style for strings
        Keyword: "ansiyellow",  # style for keywords (true, false, null in JSON)
        Literal: "ansimagenta",  # style for literals
    }


def pretty_json(
    data: dict,
    indent: int = 4,
    colored: bool = True,
    style: Type[Style] = DefaultJsonStyle,  # Specify the type of the 'style' argument
) -> str:
    """
    Return a pretty formatted JSON string.

    Args:
        data (dict): JSON data.
        indent (int): Indentation level, has to be between 2 and 8. Defaults to 4.
        colored (bool): Whether to colorize the JSON string. Defaults to True.
        style (Type[Style]): Custom style for colorizing the JSON string. Defaults to DefaultJsonStyle.
        colored (bool): Whether to colorize the JSON string. Defaults to True.

    Raises:
        ValueError: If indent is not between 2 and 8.

    Returns:
        str: Pretty formatted JSON string.
    """
    if not (2 <= indent <= 8):
        raise ValueError("Indent must be between 2 and 8.")

    formatted_json = json.dumps(data, indent=indent)
    if colored:
        formatted_json = highlight(formatted_json, JsonLexer(), TerminalFormatter(style=DefaultJsonStyle))

    return formatted_json


# Test data
data = {
    "name": "John Doe",
    "age": 30,
    "is_employee": True,
    "skills": ["Python", "Machine Learning", "Web Development"],
}


def main():
    """Print pretty JSON."""
    colorful_json = pretty_json(data)
    print(colorful_json)


if __name__ == "__main__":
    main()
