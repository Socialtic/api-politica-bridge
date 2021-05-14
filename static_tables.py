from sheets import sheet_reader
from utils import colors_to_list, make_banner, make_table, write_csv

SHEET_ID = "1fKXpwXhKlLLG-kjh8udQIH9poNLs7kAzSnXndZ1Le4Y"
CSV_DB_PATH = 'csv_db'

# Struct read ranges
ST_RANGES = {
    "area": "B1:H376", "chamber": "B1:C358", "role": "B1:F358",
    "coalition": "B1:D37", "party": "B1:F78",
    "profession": "B1:B119", "contest": "B1:G358"
    # "past-membership": "A1:G1",
    }

make_banner("Getting static tables data")
# AREA
area_data = sheet_reader(SHEET_ID, f"Table area!{ST_RANGES['area']}")
area_header = area_data[0].keys()
write_csv(make_table(area_header, area_data), f"{CSV_DB_PATH}/area")
# CHAMBER
chamber_data = sheet_reader(SHEET_ID, f"Table chamber!{ST_RANGES['chamber']}")
chamber_header = chamber_data[0].keys()
write_csv(make_table(chamber_header, chamber_data), f"{CSV_DB_PATH}/chamber")
# ROLE
role_data = sheet_reader(SHEET_ID, f"Table role!{ST_RANGES['role']}")
role_header = role_data[0].keys()
write_csv(make_table(role_header, role_data), f"{CSV_DB_PATH}/role")
# COALITION
coalition_data = sheet_reader(SHEET_ID,
                              f"Table coalition!{ST_RANGES['coalition']}")
coalition_header = coalition_data[0].keys()
write_csv(make_table(coalition_header, coalition_data),
          f"{CSV_DB_PATH}/coalition")
coalition_data = colors_to_list(coalition_data)
coalitions_catalogue = sheet_reader(SHEET_ID, "Table coalition!B2:B37",
                                    as_list=True)
# PARTY
party_data = sheet_reader(SHEET_ID, f"Table party!{ST_RANGES['party']}")
party_header = party_data[0].keys()
write_csv(make_table(party_header, party_data), f"{CSV_DB_PATH}/party")
party_data = colors_to_list(party_data)
parties = sheet_reader(SHEET_ID, "Table party!C2:C78", as_list=True)
# CONTEST
contest_data = sheet_reader(SHEET_ID, f"Table contest!{ST_RANGES['contest']}")
contest_header = contest_data[0].keys()
write_csv(make_table(contest_header, contest_data), f"{CSV_DB_PATH}/contest")
contest_chambers = sheet_reader(SHEET_ID, "Table contest!C2:C358",
                                as_list=True)
# PROFESSION
profession_range = f"Catalogue profession!{ST_RANGES['profession']}"
profession_data = sheet_reader(SHEET_ID, profession_range)
profession_header = profession_data[0].keys()
write_csv(make_table(profession_header, profession_data),
          f"{CSV_DB_PATH}/profession")
professions_catalogue = sheet_reader(SHEET_ID, "Catalogue profession!B2:B119",
                                     as_list=True)
# URL types Catalogue
url_types = sheet_reader(SHEET_ID, "Catalogue url_types!B2:B23", as_list=True)
