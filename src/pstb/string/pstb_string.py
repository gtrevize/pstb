"""
String utilities.

Functions:
    dict_to_csv_str(data: list[dict], field_names: list | None = None, column_headers: bool = True,
    quoting: int = csv.QUOTE_MINIMAL, quote_char: str = '"', delimiter: str = ",",) -> str

    dict_to_html_str(data: dict | list, indent: int = 2) -> str

    text_to_list(text: str) -> list[float] -> list[int]

"""

import csv
import io
import re

# cspell: disable-next-line
from sympy.ntheory import isprime


def dict_to_csv_str(
    data: list[dict],
    field_names: list | None = None,
    column_headers: bool = True,
    quoting: int = csv.QUOTE_MINIMAL,
    quote_char: str = '"',
    delimiter: str = ",",
) -> str:
    """
    Convert a dictionary to a CSV string.
    You can selected which fields to include in the CSV string by specifying a list of field names.
    Column headers are included by default.

    Args:
        data (list): List of dictionaries.
        field_names (list, optional): List of field names (column headers). Defaults to None.
        column_headers (bool, optional): Whether to include column headers. Defaults to True.
        quoting (int, optional): Quoting style. Defaults to csv.QUOTE_MINIMAL.
        quote_char (str, optional): Quote character. Defaults to '"'.
        delimiter (str, optional): Delimiter. Defaults to ",".

    Raises:
        ValueError: If an invalid quoting style is specified.

    Returns:
        str: CSV string.
    """
    if quoting not in [csv.QUOTE_ALL, csv.QUOTE_MINIMAL, csv.QUOTE_NONE, csv.QUOTE_NONNUMERIC]:
        raise ValueError(
            "Invalid quoting style. Valid styles are: QUOTE_ALL, QUOTE_MINIMAL, QUOTE_NONE, QUOTE_NONNUMERIC"
        )

    # Use StringIO to capture CSV data as a string
    output = io.StringIO()

    # Create a DictWriter object, specify fieldnames (column headers)
    if field_names:
        writer = csv.DictWriter(
            output, fieldnames=field_names, quoting=quoting, quotechar=quote_char, delimiter=delimiter
        )
    else:  # If field names are not specified, use the keys of the first dictionary
        writer = csv.DictWriter(
            output, fieldnames=data[0].keys(), quoting=quoting, quotechar=quote_char, delimiter=delimiter
        )

    # Write the header (column names)
    if column_headers:
        writer.writeheader()

    # Write the data rows
    for row in data:
        writer.writerow(row)

    # Retrieve the CSV string
    csv_string = output.getvalue()

    return csv_string


def dict_to_html_str(data: dict | list, indent: int = 2) -> str:
    """
    Convert a dictionary to an HTML string.
    Keys are displayed in bold.
    This function is recursive, so it can handle nested dictionaries and lists.

    Args:
        data (dict | list): Dictionary or list.
        indent (int, optional): Indentation level, must be between 0 and 8. Defaults to 2.

    Raises:
        ValueError: If indent is not between 0 and 8.

    Returns:
        str: HTML string.
    """

    if not (0 <= indent <= 8):
        raise ValueError("Indent must be between 0 and 8.")

    if isinstance(data, dict):
        html = "<ul>\n"
        for key, value in data.items():
            html += f"  <li><strong>{key}:</strong> "
            if isinstance(value, (dict, list)):
                # Recursively process nested dictionaries or lists
                html += dict_to_html_str(value)
            else:
                # Process simple values
                html += str(value)
            html += "</li>\n"
        html += "</ul>\n"
    elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
        # Create a table for a list of dictionaries
        if data:
            html = "<table border='1'>\n<tr>"
            # Table headers
            for key in data[0].keys():
                html += f"<th>{key}</th>"
            html += "</tr>\n"
            # Table rows
            for item in data:
                html += "<tr>" + "".join(f"<td>{item[key]}</td>" for key in item.keys()) + "</tr>\n"
            html += "</table>\n"
        else:
            html = "<p>List is empty</p>\n"
    else:
        # Handle empty lists or non-dictionary items in lists
        html = "<p>" + str(data) + "</p>\n"

    return html


def text_to_list(text):
    """
    Convert a string to a list of numbers.
    Supports range notation, comparison operators, and modifiers and exclusions.

    Args:
        text (str): Input string denoting a number range.

    Returns:
        list: List of numbers.

    Raises:
        ValueError: If range notation is mixed with comparison operators.
        ValueError: If invalid range notation is used.

    Note:
        The valid syntax for range notation is:

        "1-10" -> Range from 1 to 10, inclusive.

        "~5-10" -> Exclude range from 5 to 10, inclusive.

        "1-10, ~5-8" -> Range from 1 to 10, excluding range from 5 to 8.

        "1-10, ~5-8, >=7" -> Range from 1 to 10, excluding range from 5 to 8, and including numbers
        greater than or equal to 7.

        "1-10, ~5-8, >=7:odd" -> Range from 1 to 10, excluding range from 5 to 8, including numbers greater than or
        equal to 7, and only odd numbers.

        "1-10, ~5-8, >=7:odd,step=2" -> Range from 1 to 10, excluding range from 5 to 8, including numbers greater than
        or equal to 7, only odd numbers, and step of 2.

        "1-10, ~5-8, >=7:odd,step=2,div=3" -> Range from 1 to 10, excluding range from 5 to 8, including numbers
        greater than or equal to 7, only odd numbers, step of 2, and divisible by 3.

        "1-10, ~5-8, ~3" -> Range from 1 to 10, excluding range from 5 to 8, and excluding 3.

        "1-10, ~5-8, ~3-6" -> Range from 1 to 10, excluding range from 5 to 8, excluding range from 3 to 6.

        The valid modifiers are:

        - "odd" -> Only odd numbers.
        - "even" -> Only even numbers.
        - "step=2" -> Step of 2.
        - "div=3" -> Divisible by 3.

    Warning:
        - Comparison operators (<, <=, >, >=) can be used in combination with the exclusion operator (~)
          in the same string.
        - However, when using comparison operators with the exclusion operator, it is important to ensure that the
          range notation ('-') is not mixed with the comparison operators.
        - If range notation is mixed with comparison operators without the exclusion operator,
          a ValueError will be raised.


    Examples:
            "1-10" -> [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

            "1-10, 20-30" -> [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, ..., 30]

            "1-10, ~5-8" -> [1, 2, 3, 4, 9, 10]

            "1-10, ~5-8, >=7" -> [1, 2, 3, 4, 9, 10, 7, 8]

            "1-10, ~5-8, >=7:odd" -> [1, 3, 9, 7]

            "1-10, ~5-8, >=7:odd,step=2" -> [1, 9]

            "1-10, ~5-8, >=7:odd,step=2,div=3" -> [9]

            "1-10, ~5-8, ~3" -> [1, 2, 4, 5, 6, 7, 8, 9, 10]

            "1-10, ~5-8, ~3-6" -> [1, 2, 4, 5, 9, 10]

            "1-10, ~5-8, <3, >7" -> [1, 2, 8, 9, 10]

            "1-10, ~5-8, <3, >7:even" -> [2, 8, 10]
    """

    # Separate the range string and the modifiers
    if ":" in text:
        range_string, modifier_string = text.split(":", 1)
    else:
        range_string, modifier_string = text, ""

    # Find all patterns in the range string
    patterns = re.findall(r"(\d+)-(\d+)|(\d+)|([<>]=?\d+)|(~\d+-\d+)|(~\d+)", range_string)

    # Validation for mixing range notation with comparison operators
    if (
        any("-" in part for part in range_string.split(","))
        and any(op in range_string for op in ["<", "<=", ">", ">="])
        and not all("~" in part for part in range_string.split(","))
    ):
        raise ValueError(
            """Range notation '-' cannot be combined with comparison operators '<', '<=', '>', '>=' unless it's part of
            an exclusion range '~'"""
        )

    result = set()  # Using a set to avoid duplicates

    # Process the range patterns
    for p in patterns:
        if p[0] and p[1]:  # Range like "1-10"
            result.update(range(int(p[0]), int(p[1]) + 1))
        elif p[2]:  # Single number like "12"
            result.add(int(p[2]))
        elif p[3]:  # Conditions like "<=100" or ">=10"
            # Extract the comparison operator and number
            match = re.match(r"([<>]=?)(\d+)", p[3])
            if match:
                comp_op, number = match.groups()
                number = int(number)

                # Generate range based on the comparison operator
                if comp_op == "<=":
                    result.update(range(1, number + 1))
                elif comp_op == ">=":
                    # Assuming a large number for the upper limit
                    result.update(range(number, 10000))
        elif p[4]:  # Exclude subrange like "~10-20"
            start, end = map(int, p[4][1:].split("-"))
            result.difference_update(range(start, end + 1))
        elif p[5]:  # Exclude single number like "~13"
            result.discard(int(p[5][1:]))

    # Process the modifiers
    modifiers = modifier_string.split(",")
    for mod in modifiers:
        if mod == "odd":
            result = {x for x in result if x % 2 != 0}
        elif mod == "even":
            result = {x for x in result if x % 2 == 0}
        elif mod == "prime":
            result = {x for x in result if isprime(x)}
        elif mod.startswith("step"):
            step = int(re.findall(r"\d+", mod)[0]) if re.findall(r"\d+", mod) else 1
            result = {x for i, x in enumerate(sorted(result)) if i % step == 0}
        elif mod.startswith("div"):
            divisor = int(re.findall(r"\d+", mod)[0]) if re.findall(r"\d+", mod) else 7
            result = {x for x in result if x % divisor == 0}

    return sorted(result)


# Example usage
try:
    print(text_to_list("1-100, ~10-20, >=30:even,step=2"))  # Apply even, step modifiers and exclude range 10-20
except ValueError as e:
    print(f"Error: {e}")


# Sample data: List of dictionaries
data = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "Los Angeles"},
    {"name": "Charlie", "age": 35, "city": "Chicago"},
]

# Example data
data_html = {
    "Name": "Alice",
    "Age": 30,
    "Skills": [{"Skill": "Python", "Level": "Intermediate"}, {"Skill": "Data Analysis", "Level": "Beginner"}],
}


def main():
    # Convert to CSV
    csv_string = dict_to_csv_str(data)
    print(csv_string)

    # Convert to HTML
    html_output = dict_to_html_str(data_html)
    print(html_output)


if __name__ == "__main__":
    main()
