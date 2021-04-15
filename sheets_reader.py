from auth import spreadsheet_service

# Get Google spreadsheets service
sheet = spreadsheet_service.spreadsheets()

def get_sheets_data(sheet_id, read_range):
    result = sheet.values().get(spreadsheetId=sheet_id, range=read_range).execute()
    values = result.get('values', [])
    return values if values else []