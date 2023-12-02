"""
String utilities.

Functions:
    dict_to_csv_str: Convert a dictionary to a CSV string.
    dict_to_html_str: Convert a dictionary to an HTML string.

"""

import csv
import io


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
