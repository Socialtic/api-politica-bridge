import logging
import re
from datetime import datetime
from csv_diff import load_csv, compare
from sheets import sheet_reader
from static_tables import (area_data, chamber_data, role_data, coalition_data,
                           coalitions_catalogue, party_data, parties,
                           contest_data, contest_chambers, profession_data,
                           professions_catalogue, url_types)
from utils import (make_table, write_csv, make_banner, update_data, read_csv,
                   row_to_dict, send_data, make_person_struct,
                   make_other_names_struct, make_person_profession,
                   make_membership, make_url_struct, get_capture_lines,
                   verification_process, update_url_data, update_person_data,
                   update_membership_data, update_profession_data,
                   update_other_name_data, get_update_week, get_urls)


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


SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
DATA_PATH = 'dataset'
API_BASE = "http://localhost:5000/"
PERSON_RANGE = "Todos!A1:AG3220"
COALITION_URL_RANGE = "URL_logo_partido_coal!A1:H37"
PARTY_URL_RANGE = "URL_logo_partido_coal!I1:R62"
RANGES = {
    "person": PERSON_RANGE, "party_urls": PARTY_URL_RANGE,
    "coalition_urls": COALITION_URL_RANGE
}

url_pattern = r'(^Website$|^source_of_truth$|^URL_(\w)*$)'
profession_pattern = r'^profession_[2-6]$'

URLS = get_urls(API_BASE)
WEEK = get_update_week()

def main():
    make_banner(f"Checking for updates")
    for name, read_range in RANGES.items():
        dataset = sheet_reader(SHEET_ID, read_range)
        header = dataset[0].keys()
        table = make_table(header, dataset)
        write_csv(table, f"{name}_current", path=DATA_PATH)
        if name == "person":
            print(f"\t * Test {len(dataset)} rows")
            error_lines = verification_process(dataset, header)
            if error_lines:
                # Writing report
                date = datetime.now()
                str_date = date.strftime("%y-%b-%d")
                write_csv("\n".join(error_lines), f"{str_date}_errors",
                        path="errors")
                print(f"\n\t ** {len(error_lines)} fails **")
            else:
                print("\t OK. ")
        diff = compare(
            load_csv(open(f'{DATA_PATH}/{name}_old.csv'), key=f'{name}_id'),
            load_csv(open(f'{DATA_PATH}/{name}_current.csv'), key=f'{name}_id'),
        )
        breakpoint()
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


def send_changes(changed):
    for row in changed:
        for field, changes in row["changes"].items():
            data = {
                "person_id": row["key"],
                "field": field,
                "old": changes[0],
                "new": changes[1],
            }
            # first_name, last_name, full_name, date_birth, gender,
            # dead_or_alive, last_degree_of_studies, nickname, state, area
            if field in ["first_name", "last_name", "full_name", "date_birth",
                         "gender", "dead_or_alive", "last_degree_of_studies",
                         "state", "area"]:
                update_person_data(data, API_BASE, update_logger)
            elif field == "nickname":
                update_other_name_data(data, API_BASE)
            # profession_[2-6]
            elif re.search(profession_pattern, field):
                update_profession_data(data, API_BASE)
            # Website, URL_FB_page, URL_FB_profile, URL_IG, URL_TW, URL_others,
            # URL_photo, source_of_truth
            elif re.search(url_pattern, field):
                update_url_data(data, API_BASE, URLS, url_types, update_logger)
            # start_date, end_date, membership_type, is_substitute,
            elif field in ["start_date", "end_date", "membership_type",
                           "is_substitute", "abbreviation", "coalition"]:
                update_membership_data(data, API_BASE)
            log_msg = f"""{WEEK},{field},{data['person_id']},"{data['old']}","{data['new']}" """
            update_logger.info(log_msg)


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
        add_logger.info(f"{WEEK},{line}")


def log_deletes(deletes):
    for line in get_capture_lines(deletes):
        deletes_logger.info(f"{WEEK},{line}")


if __name__ == "__main__":
    main()
