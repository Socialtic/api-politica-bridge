from sheets_reader import get_sheets_data
from validations import (lastname_check, membership_type_check,
                        date_format_check, url_check, profession_check)
from utils import (make_banner, get_professions, get_urls, get_dates)

SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
READ_RANGES = ["Gubernaturas_Gisela!A1:AI114", "Gubernaturas_Celso!A1:AH115",
               "PMun_Gisela!A1:AJ119", "PMun_Emma!A1:AJ61",
               "PMun_Celso!A1:AJ81", "PMun_Bianca!A1:AJ119"]

def main():
    for read_range in READ_RANGES[:1]:
        data = get_sheets_data(SHEET_ID, read_range)
        header = data.pop(0)
        for row in data:
            make_banner(f"Runing test suite for {read_range}")
            print("* Check lastname:", lastname_check(row[2]))
            print("* Check membership", membership_type_check(row[8]))
            print("** Check dates **")
            dates_index = [9, 10, 12]
            dates = get_dates(row, dates_index)
            for i, date in zip(dates_index, dates):
                print(f"\t* Check {header[i]}: {date_format_check(date)}")
            urls = get_urls(row)
            print("** Check URLS **")
            for i, url in zip(range(22, 29), urls):
                print(f"\t* Check {header[i]}: {url_check(url)}")
            professions = get_professions(row)
            print("* Check duplicate professions:", profession_check(professions))


if __name__ == "__main__":
    main()