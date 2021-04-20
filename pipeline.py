from sheets_reader import get_sheets_data
from utils import (make_banner, get_columns_data, row_to_dict,
                   verification_process, write_report, my_str_to_bool,
                   make_table, get_contest_id, get_role_name, get_contest_name,
                   make_person_struct, make_other_names_struct,
                   make_person_profession, make_membership, get_row_urls,
                   get_url_type_id, make_url_struct)

CAPTURE_SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
STRUCT_SHEET_ID = "1fKXpwXhKlLLG-kjh8udQIH9poNLs7kAzSnXndZ1Le4Y"
# Ranges of the sheet to be read
READ_RANGES = ["Gubernaturas!A1:AB114", "Alcaldías!A1:AC63"]
# Only test in this columns
TEST_FIELDS = ["last_name", "membership_type", "start_date", "end_date",
               "date_birth", "profession_2", "profession_3",
               "profession_4", "profession_5", "profession_6", "Website",
               "URL_FB_page", "URL_FB_profile", "URL_IG", "URL_TW",
               "URL_others"]
CONTEST_CHAMBERS = get_sheets_data(STRUCT_SHEET_ID, "Table contest!C2:C357")

# REPORT_PATH = "reports"
# TABLES_PATH = "structured_tables"


def main():
    # Main loop throught sheet pages
    for read_range in READ_RANGES[:1]: # Testing only on Gubernaturas
        current_chamber = read_range.split('!')[0].lower()
        make_banner(f"Data from >> {current_chamber}")
        # Getting sheet data as list of list
        dataset = get_sheets_data(CAPTURE_SHEET_ID, read_range)
        # Ignoring header
        header = dataset.pop(0)
        # Removing start and end spaces of header items
        header = [h.strip() for h in header]
        # Convert list to dict
        dict_dataset = [row_to_dict(row, header) for row in dataset]
        # Start capture verification
        make_banner("Tests Suite begin")
        error_lines = verification_process(dataset, header)
        if error_lines:
            # Writing report
            write_report("\n".join(error_lines),
                         f"{current_chamber}_errors")
        make_banner("Preprocessing Data")
        # Making structured data
        # TODO: Get the information of tables that are already finished
        # TODO: area, chamber, role, coalition, party, contest(?),
        # TODO: Make this dynamic
        # Ignoring last 's' from gubernaturas
        #current_chamber = current_chamber[:-1]
        # Making person data
        person_header = ["full_name", "first_name", "last_name", "date_birth",
                         "gender", "dead_or_alive", "last_degree_of_studies",
                         "contest_id"]
        # This list is ready to be send to the API
        person_data = make_person_struct(dict_dataset, current_chamber,
                                    CONTEST_CHAMBERS, person_header)
        # Making a table for double check
        person_table = make_table(person_header, person_data)
        write_report(person_table, f"person")
        # Making other-name data
        other_name_header = ["other_name_type", "name", "person_id"]
        # This list is ready to be send to the API
        other_names_data = make_other_names_struct(dict_dataset)
        # Making a table for double check
        other_name_table = make_table(other_name_header, other_names_data)
        write_report(other_name_table, f"other-name")
        # Making person-profession data
        person_profession_header = ["person_id", "profession_id"]
        professions_catalogue = get_sheets_data(STRUCT_SHEET_ID,
                                               "Catalogue profession!B2:B120")
        person_profession_data = make_person_profession(dict_dataset,
                                                        professions_catalogue)
        person_profession_table = make_table(person_profession_header,
                                             person_profession_data)
        write_report(person_profession_table, f"person-profession")
        # Making membership data
        membership_header = ["person_id", "role_id", "party_id",
                             "coalition_id", "contest_id", "goes_for_coalition",
                             "membership_type", "goes_for_reelection",
                             "start_date", "end_date", "is_substitute",
                             "parent_membership_id", "changed_from_substitute",
                             "date_changed_from_substitute"]
        parties = get_sheets_data(STRUCT_SHEET_ID,
                                  "Table party!C2:C96")
        coalitions = get_sheets_data(STRUCT_SHEET_ID, "Table coalition!B2:B36")
        membership_data = make_membership(dict_dataset, current_chamber,
                                          parties, coalitions, CONTEST_CHAMBERS,
                                          membership_header)
        membership_table = make_table(membership_header, membership_data)
        write_report(membership_table, f"membership")
        # Making url data
        url_header = ["url", "description", "url_type", "owner_type",
                      "owner_id"]
        url_types = get_sheets_data(STRUCT_SHEET_ID,
                                    "Catalogue url_types!B2:B23")
        url_data = make_url_struct(dict_dataset, url_types)
        url_table = make_table(url_header, url_data)
        write_report(url_table, f"url")
        make_banner("FINISH")


if __name__ == "__main__":
    main()
