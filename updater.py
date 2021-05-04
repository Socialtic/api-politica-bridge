import os
from csv_diff import load_csv, compare
from sheets import sheet_reader
#from static_tables import (area_data, chamber_data, role_data, coalition_data,
#                           coalitions_catalogue, party_data, parties,
#                           contest_data, contest_chambers, profession_data)
from utils import changes_tracker, make_table, write_csv, make_banner, send_new_data

SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
DATA_PATH = 'dataset/'
API_BASE = "http://localhost:5000/"

def main():
    dataset = sheet_reader(SHEET_ID, "TODO!A1:AF2347")
    header = dataset[0].keys()
    table = make_table(header, dataset)
    write_csv(table, f"{DATA_PATH}current")
    if not os.path.isfile('dataset/old.csv'):
        write_csv(table, f"{DATA_PATH}/old")
        print("ALL IS UPDATED :)")
        return 0
    diff = compare(
        load_csv(open(f'{DATA_PATH}old.csv'), key='person_id'),
        load_csv(open(f'{DATA_PATH}current.csv'), key='person_id'),
    )

    if diff["changed"]:
        make_banner("There are changes :O")
        result_set = []
        data = dict()
        for change_data in diff["changed"]:
            person_id = change_data["key"]
            changed_fields = change_data["changes"].keys()
            for field in changed_fields:
                changes = change_data["changes"][field]
                send_new_data(field, changes, API_BASE, dataset, person_id)
                data[f"{field}_old"] = change_data["changes"][field][0]
                data[field] = change_data["changes"][field][1]
            result_set.append(data.copy())
            data = dict()
    print(diff)


if __name__ == "__main__":
    main()
