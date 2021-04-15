import csv
from sheets_reader import get_sheets_data
from validations import (last_name_check, membership_type_check,
                        date_format_check, url_check, profession_check, url_other_check)
from utils import (make_banner, row_to_dict, get_columns_data, write_report)

SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
# Ranges of the sheet to be read
READ_RANGES = ["Gubernaturas!A1:AB114",]
# Only test in this columns
TEST_FIELDS = ["last_name", "membership_type", "start_date", "end_date",
                "date_birth", "profession_2", "profession_3",
                "profession_4", "profession_5", "profession_6", "Website",
                "URL_FB_page", "URL_FB_profile", "URL_IG", "URL_TW", "URL_others"]

def main():
    # Main loop throught sheet pages
    for read_range in READ_RANGES:
        make_banner(f"Runing test suite for {read_range}")
        # Getting sheet data as list of list
        dataset = get_sheets_data(SHEET_ID, read_range)
        # Ignoring header
        header = dataset.pop(0)
        # Removing start and end spaces of header items
        header = [h.strip() for h in header]
        lines = []
        # Loop to read every row
        for i, row in enumerate(dataset, start=2):
            print(f"Checking row #{i} = {row[3]}")
            line = f'{i}'
            # Change row from list to dict with relevant information (test fields)
            data = row_to_dict(row, header, TEST_FIELDS)
            # Tests suite start
            line += ",last_name" if not last_name_check(data["last_name"] or []) else ""
            line += ",membership_type" if not membership_type_check(data["membership_type"]) else ""
            line += ",start_date" if not date_format_check(data["start_date"]) else ""
            line += ",end_date" if not date_format_check(data["end_date"]) else ""
            line += ",date_birth" if not date_format_check(data["date_birth"]) else ""
            professions = get_columns_data(data, "profession")
            line += ",professions" if not profession_check(professions.values()) else ""
            line += ",Website" if not url_check(data["Website"], "light") else ""
            line += ",URL_FB_page" if not url_check(data["URL_FB_page"], "strict") else ""
            line += ",URL_FB_profile" if not url_check(data["URL_FB_profile"], "strict") else ""
            line += ",URL_IG" if not url_check(data["URL_IG"], "strict") else ""
            line += ",URL_TW" if not url_check(data["URL_TW"], "strict") else ""
            url_others = data["URL_others"].split(",")
            line +=  url_other_check(url_others)
            # If no errors, discard this line
            if line == str(i):
                continue
            # Adding candidate name at the end of the line
            else:
                line += f",{row[3]}"
            lines.append(line)
        # Writing report
        write_report("\n".join(lines))

if __name__ == "__main__":
    main()