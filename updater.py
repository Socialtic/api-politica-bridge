import os
import logging
from csv_diff import load_csv, compare
from sheets import sheet_reader
from static_tables import (area_data, chamber_data, role_data, coalition_data,
                           coalitions_catalogue, party_data, parties,
                           contest_data, contest_chambers, profession_data,
                           professions_catalogue, url_types)
from utils import (make_table, write_csv, make_banner, update_data, read_csv,
                   row_to_dict, send_data, make_person_struct,
                   make_other_names_struct, make_person_profession,
                   make_membership, make_url_struct, get_capture_lines)

# Updates logger
update_logger = logging.getLogger("updates")
update_logger.setLevel(logging.INFO)

# Aditions logger
add_logger = logging.getLogger("additions")
add_logger.setLevel(logging.INFO)

# Delete logger
deletes_logger = logging.getLogger("deletes")
deletes_logger.setLevel(logging.INFO)

# Setting log format
log_format = logging.Formatter("%(levelname)s,%(asctime)s,%(message)s",
                                datefmt="%d/%b/%y %H:%M:%S")

# Update file handler
update_file = logging.FileHandler("logs/updates.log")
update_file.setLevel(logging.INFO)
update_file.setFormatter(log_format)

# Adition file handler
add_file = logging.FileHandler("logs/aditions.log")
add_file.setLevel(logging.INFO)
add_file.setFormatter(log_format)

# Deletes file handler
deletes_file = logging.FileHandler("logs/deletes.log")
deletes_file.setLevel(logging.INFO)
deletes_file.setFormatter(log_format)

# Stream handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(log_format)

# Adding handlers to loggers
update_logger.addHandler(update_file)
update_logger.addHandler(stream_handler)

add_logger.addHandler(add_file)
add_logger.addHandler(stream_handler)

deletes_logger.addHandler(deletes_file)
deletes_logger.addHandler(stream_handler)

#logging.basicConfig(level=logging.INFO, filename="logs/updater.log",
#                    datefmt="%d/%b/%y %H:%M:%S",
#format="%(levelname)s,%(asctime)s,%(message)s")

SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
DATA_PATH = 'dataset/'
API_BASE = "http://localhost:5000/"
# TODO: Dynamicaly change over the time
WEEK = 2

local = True


def send_changes(changed):
    for row in changed:
        person_id = row["key"]
        fields = row["changes"].keys()
        for field in fields:
            changes = row["changes"][field]
            old = changes[0]
            new = changes[1]
            log_msg = f"CHANGE,{WEEK},{person_id},{old},{new},{field}"
            update_logger.info(log_msg)
            # r = update_data(field, changes, API_BASE, dataset, person_id)


def send_additions(added):
    # PERSON
    person_header = ["full_name", "first_name", "last_name", "date_birth",
                     "gender", "dead_or_alive", "last_degree_of_studies",
                     "contest_id"]
    person_data = make_person_struct(added, contest_chambers, person_header)
    print("\t * SENDING PERSON DATA")
    send_data(API_BASE, 'person', person_data)

    # OTHER-NAME (optional)
    other_names_data = make_other_names_struct(added)
    if other_names_data:
        print("\t * SENDING OTHER-NAME DATA")
        send_data(API_BASE, 'other-name', other_names_data)

    #  PERSON-PROFESSION (optional)
    person_profession_data = make_person_profession(added,
                                                    professions_catalogue)
    if person_profession_data:
        print("\t * SENDING PERSON-PROFESSION DATA")
        send_data(API_BASE, 'person-profession', person_profession_data)

    # MEMBERSHIP
    membership_header = ["person_id", "role_id", "party_id",
                         "coalition_id", "contest_id",
                         "goes_for_coalition", "membership_type",
                         "goes_for_reelection",
                         "start_date", "end_date", "is_substitute",
                         "parent_membership_id", "changed_from_substitute",
                         "date_changed_from_substitute"]
    membership_data = make_membership(added, parties, coalitions_catalogue,
                                      contest_chambers, membership_header)
    print("\t * SENDING MEMBERSHIP DATA")
    send_data(API_BASE, 'membership', membership_data)

    # URL
    url_data = make_url_struct(added, url_types)
    if url_data:
        print("\t * SENDING URL DATA")
        send_data(API_BASE, 'url', url_data)
    lines = get_capture_lines(added)
    print()
    for line in lines:
        add_logger.info(f"ADD,{WEEK},{line}")


def log_deletes(deletes):
    for line in get_capture_lines(deletes):
        deletes_logger.info(f"DELETE,{WEEK},{line}")


def main():
    make_banner(f"Checking for updates | LOCAL: {local}")
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
    diff = compare(
        load_csv(open(f'{DATA_PATH}old.csv'), key='person_id'),
        load_csv(open(f'{DATA_PATH}current.csv'), key='person_id'),
    )
    if diff["changed"]:
        make_banner("There are changes")
        send_changes(diff["changed"])
    if diff["added"]:
        make_banner("There are additions")
        send_additions(diff["added"])
    if diff["removed"]:
        make_banner("There are deletes")
        log_deletes(diff["removed"])
    make_banner("Finish, have a nice day :D")


if __name__ == "__main__":
    main()
