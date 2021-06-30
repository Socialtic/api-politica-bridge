from auth import spreadsheet_service
from utils import row_to_dict

# Get Google spreadsheets service
sheet = spreadsheet_service.spreadsheets()


def sheet_reader(sheet_id, read_range, as_list=False):
    """**Read information of a given Google Sheet**

    :param sheet_id: Sheet identificator. Can be founded in the url.
    :type sheet_id: str
    :param read_range: Absolute range of cells to be read. Must be in A1 notation
    :type read_range: str
    :param as_list: Return the results as a list instead of a dicttionary, defaults to False
    :type as_list: bool, optional
    :return: Dict with header as keys and row as values
    :rtype: dict
    """
    print(f"\t\t* Reading {read_range.split('!')[0]}")
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=read_range).execute()
    values = result.get('values', [])
    if as_list:
        return [v[0].lower().strip() for v in values] if values else []
    else:
        header = values.pop(0)
        if values:
            return [row_to_dict(row, header) for row in values]
        else:
            return []
