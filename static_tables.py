from sheets import sheet_reader
from utils import colors_to_list, make_banner, make_table, write_csv

SHEET_ID = "1W8F9cf88hRXPEeLQEVbXHtQ2K6BnoXRD9vRDWL3Qpeg"
CSV_DB_PATH = 'csv_db'

# Struct read ranges
ST_RANGES = {
    "area": "A1:H111", "chamber": "A1:C111", "role": "A1:F111",
    "coalition": "A1:D68", "party": "A1:F293",
    "profession": "A1:B119", "contest": "A1:G111"
    # "past-membership": "A1:G1",
    }

make_banner("Getting static tables data")
# AREA
area_data = sheet_reader(SHEET_ID, f"Table area!{ST_RANGES['area']}")
area_header = area_data[0].keys()
write_csv(make_table(area_header, area_data), f"{CSV_DB_PATH}/area")
for area in area_data:
    if area["area_id"] == "":
        area["is_deleted"] = True
    del area["area_id"]

# CHAMBER
chamber_data = sheet_reader(SHEET_ID, f"Table chamber!{ST_RANGES['chamber']}")
chamber_header = chamber_data[0].keys()
write_csv(make_table(chamber_header, chamber_data), f"{CSV_DB_PATH}/chamber")
for chamber in chamber_data:
    if chamber["chamber_id"] == "":
        chamber["is_deleted"] = True
    del chamber["chamber_id"]

# ROLE
role_data = sheet_reader(SHEET_ID, f"Table role!{ST_RANGES['role']}")
role_header = role_data[0].keys()
write_csv(make_table(role_header, role_data), f"{CSV_DB_PATH}/role")
for role in role_data:
    if role["role_id"] == "":
        role["is_deleted"] = True
    del role["role_id"]

# COALITION
coalition_data = sheet_reader(SHEET_ID,
                              f"Table coalition!{ST_RANGES['coalition']}")
coalition_header = coalition_data[0].keys()
write_csv(make_table(coalition_header, coalition_data),
          f"{CSV_DB_PATH}/coalition")
coalition_data = colors_to_list(coalition_data)
for coalition in coalition_data:
    del coalition["coalition_id"]
coalitions_catalogue = sheet_reader(SHEET_ID, "Table coalition!B2:B68",
                                    as_list=True)

# PARTY
party_data = sheet_reader(SHEET_ID, f"Table party!{ST_RANGES['party']}")
party_header = party_data[0].keys()
write_csv(make_table(party_header, party_data), f"{CSV_DB_PATH}/party")
party_data = colors_to_list(party_data)
for party in party_data:
    if party["party_id"] == "":
        party["is_deleted"] = True
    del party["party_id"]
parties = sheet_reader(SHEET_ID, "Table party!B2:B293", as_list=True)

# CONTEST
contest_data = sheet_reader(SHEET_ID, f"Table contest!{ST_RANGES['contest']}")
contest_header = contest_data[0].keys()
write_csv(make_table(contest_header, contest_data), f"{CSV_DB_PATH}/contest")
for contest in contest_data:
    if contest["contest_id"] == "":
        contest["is_deleted"] = True
    del contest["contest_id"]
contest_chambers = sheet_reader(SHEET_ID, "Table contest!C2:C48",
                                as_list=True)
# PROFESSION
profession_range = f"Catalogue profession!{ST_RANGES['profession']}"
profession_data = sheet_reader(SHEET_ID, profession_range)
profession_header = profession_data[0].keys()
write_csv(make_table(profession_header, profession_data),
          f"{CSV_DB_PATH}/profession")
for profession in profession_data:
    del profession["profession_id"]
professions_catalogue = sheet_reader(SHEET_ID, "Catalogue profession!B2:B119",
                                     as_list=True)
# URL types Catalogue
url_types = sheet_reader(SHEET_ID, "Catalogue url_types!B2:B23", as_list=True)
