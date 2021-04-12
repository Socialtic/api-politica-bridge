from __future__ import print_function
from auth import spreadsheet_service

SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
GISELA_READ_RANGE = "Gubernaturas_Gisela!A1:AI110"

sheet = spreadsheet_service.spreadsheets()
result = sheet.values().get(spreadsheetId=SHEET_ID,
                            range=GISELA_READ_RANGE).execute()
values = result.get('values', [])

if not values:
    print('No data found.')
else:
    print('Data:')
    for row in values:
        print(row)
