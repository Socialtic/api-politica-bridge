from auth import spreadsheet_service
from utils import row_to_dict

# Get Google spreadsheets service
sheet = spreadsheet_service.spreadsheets()


def sheet_reader(sheet_id, read_range, as_list=False):
    print(f"\t\t* Reading {read_range.split('!')[0]}")
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=read_range).execute()
    values = result.get('values', [])
    if as_list:
        return values if values else []
    else:
        header = values.pop(0)
        if values:
            return [row_to_dict(row, header) for row in values]
        else:
            return []
