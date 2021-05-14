import os
import re
import requests
import json
from progressbar import ProgressBar
from requests import exceptions as r_excepts
from validations import (last_name_check, membership_type_check,
                         date_format_check, url_check, profession_check,
                         url_other_check)
with open("token.json", 'r') as f:
    TOKEN = json.load(f)
HEADERS = {
    "Authorization": f"{TOKEN['token_type']} {TOKEN['token_value']}"
}


class Catalogues:
    DEGREES_OF_STUDIES = ['', 'ELEMENTARY', 'HIGH SCHOOL', 'ASSOCIATE DEGREE',
                          'BACHELOR’S DEGREE',
                          'UNIVERSITY 1ST PROFESSIONAL DEGREE',
                          'MASTER DEGREE', 'PHD DEGREE']
    #   GOBERNADOR, DIPUTADO , PRESIDENTE MUNICIPAL
    DISTRICT_TYPES = ['NATIONAL_EXEC', 'REGIONAL_EXEC', 'NATIONAL_LOWER',
                      'LOCAL_EXEC']
    GENDERS = ['', 'M', 'F']
    MEMBERSHIP_TYPES = ['', 'officeholder', 'campaigning_politician',
                        'party_leader']
    # privilegiado, apodo, nombre de la boleta
    OTHER_NAMES_TYPES = ['', 'preferred', 'nickname', 'ballot_name']
    #   GOBERNADOR, DIPUTADO , PRESIDENTE MUNICIPAL
    ROLE_TYPES = ['', 'governmentOfficer', 'legislatorLowerBody',
                  'executiveCouncil']
    SPANISH_ROLES = {'governmentOfficer': "gubernatura",
                     "executiveCouncil": "presidencia",
                     "legislatorLowerBody": "diputación"}
    URL_TYPES = {"Website": "WEBSITE_OFFICIAL",
                 "URL_FB_page": "FACEBOOK_CAMPAIGN",
                 "URL_FB_profile": "FACEBOOK_PERSONAL",
                 "URL_IG": "INSTAGRAM_CAMPAIGN", "URL_TW": "TWITTER",
                 "URL_photo": "PHOTO", "source_of_truth": "SOURCE_OF_TRUTH",
                 "URL_logo": "LOGO"}


def make_banner(title):
    """**Make a banner for visual purposes**

    :param title: Messages to be highlighted
    :type: str
    """
    print()
    print("\t"*5, title)
    print("\t"*5, "-"*len(title))
    print()


def get_columns_data(data, pattern):
    """**Gets data from columns based on a text pattern**

    :param data: Current test fields of the sheet in a dict form
    :type data: dict
    :param pattern: Text pattern to be search in dict keys
    :type pattern: str
    :return: Dict with key-value that match pattern
    :rtype: dict
    """
    return {field: data[field] for field in data if pattern in field}


def row_to_dict(row, header, test_fields=[]):
    """**Converts from a row of the sheet to a python dict**

    :param row: Current row of the sheet
    :type row: list
    :param header: The header of the sheet
    :type header: list
    :return: A dict with header as keys and row as values
    :rtype: dict
    """
    data = dict()
    columns = test_fields if test_fields else header
    # Making dict with column-value pairs
    for column in columns:
        try:
            data[column] = row[header.index(column)]
        # Row is shorter than header. Last fields must be empty
        except IndexError:
            data[column] = ''
            continue
    return data


def verification_process(dataset, header):
    lines = []
    # Loop to read every row
    with ProgressBar(max_value=len(dataset)) as bar:
        for i, row in enumerate(dataset, start=1):
            if not row["person_id"]:
                continue
            line = f'{i}'
            # Tests suite start
            line += ",last_name" if not last_name_check(row["last_name"] or "") else ""
            line += ",membership_type" if not membership_type_check(row["membership_type"]) else ""
            line += ",start_date" if not date_format_check(row["start_date"], "start_end") else ""
            line += ",end_date" if not date_format_check(row["end_date"], "start_end") else ""
            line += ",date_birth" if not date_format_check(row["date_birth"], "birth") else ""
            professions = get_columns_data(row, "profession")
            # TODO: from 2 to 6 only
            line += ",professions" if not profession_check(professions.values()) else ""
            line += url_check(row["Website"].split(','), "light", "Website")
            line += url_check(row["URL_FB_page"].split(','), "strict", "URL_FB_page")
            line += url_check(row["URL_FB_profile"].split(','), "strict", "URL_FB_profile")
            line += url_check(row["URL_IG"].split(','), "strict", "URL_IG")
            line += url_check(row["URL_TW"].split(','), "strict", "URL_TW")
            line += url_other_check(row["URL_others"].split(","))
            # If no errors, discard this line
            if line == str(i):
                line = ''
                continue
            # Adding candidate name at the end of the line
            else:
                line += f",{row['full_name']}"
                lines.append(line)
            bar.update(i - 1)
    return lines


def write_csv(data, name):
    """**Write a csv file with current data**

    :param data: A comma separated string
    :type data: str
    """
    with open(f"{name}.csv", 'w', encoding="utf-8") as f:
        f.write(data)


def read_csv(file_name, path=""):
    full_path = os.path.join(path, file_name)
    with open(full_path + ".csv", "r", encoding="utf-8") as f:
        return [line.split(",") for line in f.read().rstrip("\n").split("\n")]


def make_table(header, dataset):
    table = ','.join(header) + '\n'
    for row_data in dataset:
        for field in header:
            try:
                cell = row_data[field].strip("\r\n ")
                if ',' in row_data[field] :
                    table += f'"{cell}",'
                else:
                    table += f'{cell},'
            except AttributeError:
                table += f"{row_data[field]},"
        table += '\n'
    return table


def get_contest_id(data, contest_chambers):
    # Gubernaturas
    if data["role_type"] == "governmentOfficer":
        location = data["state"].lower()
    # Alcaldías (presidencia)
    elif data["role_type"] == "executiveCouncil":
        location = data["area"].lower()
    # Diputación
    elif data["role_type"] == "legislatorLowerBody":
        location = f"distrito federal {data['area']} de {data['state'].lower()}"
    for i, contest_chamber in enumerate(contest_chambers, start=1):
        if location in contest_chamber and Catalogues.SPANISH_ROLES[data["role_type"]] in contest_chamber:
            return i
    return -1


def make_person_struct(dataset, contest_chambers, header, db_mode):
    people = []
    for data in dataset:
        row = dict()
        if db_mode == "FB" and not data["person_id"]:
            row["person_id"] = ''
        else:
            row["person_id"] = data["person_id"]
        for field in header:
            if field == "gender":
                row[field] = 2 if data[field] == "F" else 1
            elif field == "dead_or_alive":
                row[field] = True if data[field] == "Vivo" else False
            elif field == "last_degree_of_studies":
                if data[field]:
                    last_degree = data[field].upper()
                    row[field] = Catalogues.DEGREES_OF_STUDIES.index(last_degree)
                else:
                    row[field] = -1
            elif field == "contest_id":
                row[field] = get_contest_id(data, contest_chambers)
            elif field == "date_birth":
                if data[field]:
                    row[field] = data[field]
                else:
                    row[field] = '0001-01-01'
            else:
                row[field] = data[field]
        people.append(row)
    return people


def make_other_names_struct(dataset):
    result = []
    for i, data in enumerate(dataset, start=1):
        # TODO: check multinickname case
        if data["nickname"]:
            result.append({
                "other_name_type": 2, # TODO
                "name": data["nickname"],
                "person_id": i
            })
    return result


def make_person_profession(dataset, professions):
    lines = []
    pattern = r'^profession_[2-6]$'
    for i, data in enumerate(dataset, start=1):
        for field in data:
            if re.search(pattern, field):
                profession = data[field].lower()
                if profession:
                    profession_id = professions.index(profession) + 1
                    lines.append({
                        "person_id": i,
                        "profession_id": profession_id
                    })
    return lines


def make_membership(dataset, parties, coalitions, contest_chambers, header):
    lines = []
    for i, data in enumerate(dataset, start=1):
        if data["coalition"]:
            coalition_id = coalitions.index(data["coalition"].lower().strip()) + 1
        else:
            coalition_id = -1
        contest_id = get_contest_id(data, contest_chambers)
        lines.append({
            "person_id": i,
            # TODO: By now contest_id == role_id. Change soon
            "role_id": contest_id,
            "party_id": parties.index(data["abbreviation"].lower()) + 1,
            "coalition_id": coalition_id,
            "contest_id": contest_id,
            "goes_for_coalition": True if data["coalition"] else False,
            "membership_type": Catalogues.MEMBERSHIP_TYPES.index(data["membership_type"]),
            "goes_for_reelection": False,  # Always false
            "start_date": data["start_date"], "end_date": data["end_date"],
            "is_substitute": True if data["is_substitute"] == "Sí" else False,
            "parent_membership_id": i if data["is_substitute"] == "Sí" else -1,
            "changed_from_substitute": False,  # TODO:
            "date_changed_from_substitute": "0001-01-01"  # TODO:
        })
    return lines


def get_row_urls(row):
    pattern = r'(^Website$|^URL_(\w)*$)'
    return {field: row[field] for field in row if re.search(pattern, field) and field != "URL_others"}


def get_url_type_id(field, url_types, url=""):
    email_pattern = r'^[\w.+-]+@[\w-]+\.[\w.-]+$'
    if field == "URL_others":
        for u_type in url_types:
            if u_type.lower() in url:
                return url_types.index(u_type) + 1
            elif re.search(email_pattern, url):
                return url_types.index("email") + 1
        return 0
    else:
        return url_types.index(Catalogues.URL_TYPES[field].lower()) + 1


def get_owner_id(dataset, field_data, search_field):
    """TODO: Docstring for get_owner_type.
    :returns: TODO

    """
    for i, data in enumerate(dataset, start=1):
        if data[search_field].lower() == field_data.lower():
            return i
    return -1


def make_url_struct(dataset, url_types, coalitions=[], parties=[], owner_type=""):
    lines = []
    field_pattern = r'(^Website$|^URL_(\w)*$)'
    if owner_type in ["coalition", "party"]:
        for data in dataset:
            for field in data:
                if re.search(field_pattern, field):
                    if data[field]:
                        for url in data[field].split(","):
                            if owner_type == "coalition":
                                owner_id = get_owner_id(coalitions, data["Coalicion"],
                                                        "name")
                            else:
                                owner_id = get_owner_id(parties, data["Abreviacion"],
                                                        "abbreviation")
                            lines.append({
                                "url": data[field],
                                "url_type": get_url_type_id(field, url_types),
                                "description": "",
                                "owner_type": 3 if owner_type == "coalition" else 2,
                                "owner_id": owner_id
                            })
    # Person  or membership
    else:
        for i, data in enumerate(dataset, start=1):
            for field in data:
                if re.search(field_pattern, field) and field != "URL_others":
                    if data[field]:
                        for url in data[field].split(','):
                            row = {
                                    "url": data[field],
                                    "url_type": get_url_type_id(field, url_types),
                                    "description": '',  # TODO
                                    "owner_type": 4 if field == "source_of_truth" else 1,  # TODO: persona, partido, coalicion
                                    "owner_id": i
                                }
                            lines.append(row)
                elif field == "URL_others":
                    for url in data[field].split(","):
                        clean_url = url.strip()
                        if clean_url:
                            row = {
                                "url": clean_url,
                                "url_type": get_url_type_id(field, url_types, clean_url),
                                "description": '',  # TODO
                                "owner_type": 1,  # TODO: persona, partido, coalicion
                                "owner_id": i
                            }
                            lines.append(row)
    return lines


def colors_to_list(data):
    for row in data:
        colors_list = row["colors"].split(",")
        row["colors"] = [color.strip("' ") for color in colors_list]
    return data


def get_dummy_data(endpoint):
    if endpoint == "person":
        dummy_data = {
            "full_name": '',
            "first_name": '',
            "last_name": '',
            "date_birth": '0001-01-01',
            "gender": -1,
            "dead_or_alive": True,
            "last_degree_of_studies": -1,
            "contest_id": -1
        }
    elif endpoint == "other-name":
        dummy_data = {
            "other_name_type": -1,
            "name": "",
            "person_id": -1
        }
    elif endpoint == "person-profession":
        dummy_data = {
            "person_id": -1,
            "profession_id": -1
        }
    elif endpoint == "membership":
        dummy_data = {
            "person_id": -1,
            "role_id": -1,
            "party_id": -1,
            "coalition_id": -1,
            "contest_id": -1,
            "goes_for_coalition": False,
            "membership_type": -1,
            "goes_for_reelection": False,
            "start_date": "0001-01-01",
            "end_date": "0001-01-01",
            "is_substitute": False,
            "parent_membership_id": -1,
            "changed_from_substitute": False,
            "date_changed_from_substitute": "0001-01-01"
        }
    elif endpoint == "url":
        dummy_data = {
            "url": "",
            "description": "",
            "url_type": -1,
            "owner_type": -1,
            "owner_id": -1
        }
    return dummy_data



def send_data(base_url, endpoint, dataset, db_mode=''):
    full_url = base_url + endpoint + '/'
    if db_mode:
        make_banner(f"DB_MODE --> {db_mode}")
    with ProgressBar(max_value=len(dataset), redirect_stdout=True) as bar:
        for i, row in enumerate(dataset, start=1):
            if db_mode == "FB" and not row["person_id"]:
                dummy_data = get_dummy_data(endpoint)
                r = requests.post(full_url, json=dummy_data, headers=HEADERS)
                print("Dummy POST r:", r.status_code, "#", i)
                r = requests.delete(f"{full_url}{i}", headers=HEADERS)
                print("Dummy DELETE r:", r.status_code, "#", i)
                continue
            elif db_mode == "FB":
                del row["person_id"]
            try:
                # Sending row data to api
                r = requests.post(full_url, json=row, headers=HEADERS)
            except r_excepts.ConnectionError:
                print("[CONNECTION ERROR]")
                print(f"#{i} | url: {full_url} | data:{row}")
            if r.status_code != 201:
                print(f"[ERROR]: {endpoint} #{i} status code: {r.status_code}")
                print(f"msg: {r.json()['message']}")
            bar.update(i - 1)


def send_new_data(field, changes, api_base, dataset, person_id):
    url_pattern = r'(^Website$|^source_of_truth$|^URL_(\w)*$)'
    # Tables to modify: other-name
    if field == "nickname":
        endpoint = "other-name"
        r = requests.get(api_base + endpoint, headers=HEADERS)
        other_name_data = r.json()
        for name in other_name_data:
            # TODO: Multi nicknames
            if person_id == str(name["person_id"]):
                breakpoint()
                name["name"] = changes[1]
                other_type = Catalogues.OTHER_NAMES_TYPES.index(name["other_name_type_id"])
                name["other_name_type"] = other_type
                full_endpoint = f"{api_base}{endpoint}/{name['id']}"
                r = requests.put(full_endpoint, json=name, headers=HEADERS)
                return r
        breakpoint()
        # It's a new nickname
        new_data = {
            "name": changes[1],
            "other_name_type": 2, # TODO
            "person_id": person_id
        }
        r = requests.post(api_base + endpoint, json=new_data, headers=HEADERS)
        return r
    elif field in ["start_date", "end_date"]:
        endpoint = "membership"
        r = requests.get(api_base + endpoint, headers=HEADERS)
        memberships = r.json()["memberships"]
        for membership in memberships:
            if person_id == membership["person_id"]:
                membership_id = membership["id"]
                membership[field] = changes[1]
                r = requests.put(f"{api_base}{endpoint}/{membership_id}",
                                 data=membership, headers=HEADERS)
                return r
        return {"error": f"person #{person_id} not found", "success": False}
    elif re.search(url_pattern, field):
        endpoint = "url"
        r = requests.get(api_base + endpoint, headers=HEADERS)
        urls = r.json()["urls"]
        for url in urls:
            if person_id == url["owner_id"]:
                url["url"] = changes[1]
                r = requests.put(f"{api_base}{endpoint}/{membership_id}",
                                 data=url, headers=HEADERS)
        # TODO: It's a new URL
        # TODO: get URL type
    return True


def search_by_name(dataset, prediction_name):
    """TODO: Docstring for search_by_name.
    :returns: TODO

    """
    for i, row in enumerate(dataset):
        if row["full_name"] == prediction_name:
            return i + 1, row
    return -1, {}
