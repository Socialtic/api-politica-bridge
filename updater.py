from datetime import date, timedelta
from csv_diff import load_csv, compare
from sheets import sheet_reader
from static_tables import (area_data, chamber_data, role_data, coalition_data,
                           coalitions_catalogue, party_data, parties,
                           contest_data, contest_chambers, profession_data)
from utils import changes_tracker, make_table, write_csv

SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"

today = date.today().isoformat()

# TODO: Tabla unica
def main():
    dataset = sheet_reader(SHEET_ID, "Gubernaturas!B1:AC114")
    header = dataset[0].keys()
    table = make_table(header, dataset)
    write_csv(table, f"dataset/current")
    diff = compare(
        load_csv('current.csv'),
        load_csv('old.csv')
    )


if __name__ == "__main__":
    main()
