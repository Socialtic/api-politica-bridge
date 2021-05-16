import os
import logging
from csv_diff import load_csv, compare
from sheets import sheet_reader
#from static_tables import (area_data, chamber_data, role_data, coalition_data,
#                           coalitions_catalogue, party_data, parties,
#                           contest_data, contest_chambers, profession_data)
from utils import make_table, write_csv, make_banner, send_new_data, read_csv, row_to_dict

logging.basicConfig(level=logging.INFO, filename="logs/updater.log",
                    datefmt="%d/%b/%y %H:%M:%S",
                    format="%(levelname)s,%(asctime)s,%(message)s")

SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
DATA_PATH = 'dataset/'
API_BASE = "http://localhost:5000/"

local = True

def main():
    if local:
        dataset = read_csv("dataset/current")
        header = dataset.pop(0)
        dataset = [row_to_dict(row, header) for row in dataset]
    else:
        dataset = sheet_reader(SHEET_ID, "TODO!A1:AF2423")
        header = dataset[0].keys()
        table = make_table(header, dataset)
        write_csv(table, f"{DATA_PATH}current")
    if not os.path.isfile('dataset/old.csv'):
        write_csv(table, f"{DATA_PATH}/old")
        print("ALL IS UPDATED :)")
        return 0
    breakpoint()
    diff = compare(
        load_csv(open(f'{DATA_PATH}old.csv'), key='person_id'),
        load_csv(open(f'{DATA_PATH}current.csv'), key='person_id'),
    )
    if diff["changed"]:
        make_banner("There are changes :O")
        for change_data in diff["changed"]:
            person_id = change_data["key"]
            changed_fields = change_data["changes"].keys()
            for field in changed_fields:
                changes = change_data["changes"][field]
                logging.info(f"{person_id},{changes[0]},{changes[1]},{field}")
                r = send_new_data(field, changes, API_BASE, dataset, person_id)

    if diff["added"]:
        pass
    print(diff)


if __name__ == "__main__":
    main()
