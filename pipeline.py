from sheets import sheet_reader
from static_tables import (area_data, chamber_data, role_data, coalition_data,
                           coalitions_catalogue, party_data, parties,
                           contest_data, contest_chambers, profession_data,
                           professions_catalogue, url_types)
from utils import (make_banner, verification_process,
                   write_csv, make_table, make_person_struct,
                   make_other_names_struct, make_person_profession,
                   make_membership, make_url_struct, send_data)
# ID sheets
CAPTURE_SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
# Capture Read Ranges
READ_RANGE = "TODO!A1:AG2441"

API_BASE = 'http://localhost:5000/'
# API endpoints
ENDPOINTS = ["area", "chamber", "role", "coalition", "party", "person",
             "other-name", "profession", "membership", "contest", "url"]


def main():
    make_banner("VERIFICATIONS")
    #current_chamber = read_range.split('!')[0].lower()
    # Getting sheet data as list of list
    dataset = sheet_reader(CAPTURE_SHEET_ID, READ_RANGE)
    # Getting header
    header = dataset[0].keys()
    # Start capture verification
    print(f"\t * Test {len(dataset)} rows")
    error_lines = verification_process(dataset, header)
    if error_lines:
        # Writing report
        write_csv("\n".join(error_lines), "errors")
        print(f"\n\t ** {len(error_lines)} fails **")
    else:
        print(f"\t OK. ")

    # PREPROCESSING DYNAMIC DATA
    print("\t * Build dynamic data")

    # PERSON
    person_header = ["full_name", "first_name", "last_name", "date_birth",
                        "gender", "dead_or_alive", "last_degree_of_studies",
                        "contest_id"]
    # This list is ready to be send to the API
    person_data = make_person_struct(dataset, contest_chambers, person_header)
    # Making a table for double check
    person_table = make_table(person_header, person_data)
    write_csv(person_table, f"dataset/person")
    # OTHER-NAME
    other_name_header = ["other_name_type", "name", "person_id"]
    # This list is ready to be send to the API
    other_names_data = make_other_names_struct(dataset)
    # Making a table for double check
    other_name_table = make_table(other_name_header, other_names_data)
    write_csv(other_name_table, "dataset/other-name")

    #  PERSON-PROFESSION
    person_profession_header = ["person_id", "profession_id"]
    person_profession_data = make_person_profession(dataset,
                                                    professions_catalogue)
    person_profession_table = make_table(person_profession_header,
                                            person_profession_data)
    write_csv(person_profession_table, "dataset/person-profession")

    # MEMBERSHIP
    membership_header = ["person_id", "role_id", "party_id",
                            "coalition_id", "contest_id",
                            "goes_for_coalition", "membership_type",
                            "goes_for_reelection",
                            "start_date", "end_date", "is_substitute",
                            "parent_membership_id", "changed_from_substitute",
                            "date_changed_from_substitute"]
    membership_data = make_membership(dataset, parties, coalitions_catalogue,
                                      contest_chambers, membership_header)
    membership_table = make_table(membership_header, membership_data)
    write_csv(membership_table, f"dataset/membership")

    # URL
    url_header = ["url", "description", "url_type", "owner_type",
                    "owner_id"]
    url_data = make_url_struct(dataset, url_types)
    url_table = make_table(url_header, url_data)
    write_csv(url_table, f"dataset/url")
    print("\t * Ok.")

    make_banner("Sending data to API")
    # AREA
    print("\t * AREA")
    send_data(API_BASE, 'area', area_data)
    # CHAMBER
    print("\t * CHAMBER")
    send_data(API_BASE, 'chamber', chamber_data)
    # ROLE
    print("\t * ROLE")
    send_data(API_BASE, 'role', role_data)
    # COALITION
    print("\t * COALITION")
    send_data(API_BASE, 'coalition', coalition_data)
    # PARTY
    print("\t * PARTY")
    send_data(API_BASE, 'party', party_data)
    # PERSON
    print("\t * PERSON")
    send_data(API_BASE, 'person', person_data)
    # OTHER-NAME
    print("\t * OTHER-NAME")
    send_data(API_BASE, 'other-name', other_names_data)
    # PROFESSION
    print("\t * PROFESSION")
    send_data(API_BASE, 'profession', profession_data)
    # PERSON-PROFESSION
    print("\t * PERSON-PROFESSION")
    send_data(API_BASE, 'person-profession', person_profession_data)
    # MEMBERSHIP
    print("\t * MEMBERSHIP")
    send_data(API_BASE, 'membership', membership_data)
    # CONTEST
    print("\t * CONTEST")
    send_data(API_BASE, 'contest', contest_data)
    # URL
    print("\t * URL")
    send_data(API_BASE, 'url', url_data)
    make_banner("Finish. Have a nice day :)")


if __name__ == "__main__":
    main()
