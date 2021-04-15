import re

def make_banner(title):
    """**Make a banner for visual purposes**

    :param title: Messages to be highlighted   
    :type: str
    """
    print()
    print("\t"*5, title)
    print("\t"*5, "-"*len(title))
    print()


def get_columns_data(data, pattern):
    """**Gets data from columns based on a text pattern**

    :param data: Current test fields of the sheet in a dict form
    :type data: dict
    :param pattern: Text pattern to be search in dict keys
    :type pattern: str
    :return: Dict with key-value that match pattern
    :rtype: dict
    """
    return {field:data[field] for field in data if pattern in field}


def row_to_dict(row, header, test_fields):
    """**Converts from a row of the sheet to a python dict**

    :param row: Current row of the sheet
    :type row: list
    :param header: The header of the sheet
    :type header: list
    :return: A dict with header as keys and row as values
    :rtype: dict
    """
    data = dict()
    # Making dict with column-value pairs
    for column in test_fields:
        try:
            data[column] = row[header.index(column)]
        # Row is shorter than header. Last fields must be empty
        except IndexError:
            data[column] = ''
            continue 
    return data


def write_report(data):
    """**Write a report with the errors found  at the sheet**

    :param data: A comma separated string with line number and fields with errors
    :type data: str
    """
    with open("report.csv", 'w') as f:
        f.write(data)

