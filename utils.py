import re
import requests
import progressbar
from requests import exceptions as r_excepts
from validations import (last_name_check, membership_type_check,
                         date_format_check, url_check, profession_check,
                         url_other_check)


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
    URL_TYPES = {"Website": "WEBSITE_OFFICIAL",
                 "URL_FB_page": "FACEBOOK_CAMPAIGN",
                 "URL_FB_profile": "FACEBOOK_PERSONAL",
                 "URL_IG": "INSTAGRAM_CAMPAIGN", "URL_TW": "TWITTER",
                 "source_of_truth": "SOURCE_OF_TRUTH"}


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
    for i, row in enumerate(dataset, start=2):
        print(f"\t\t -> Checking row #{i} = {row['full_name']}")
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
    return lines


def write_csv(data, name):
    """**Write a csv file with current data**

    :param data: A comma separated string
    :type data: str
    """
    with open(f"{name}.csv", 'w', encoding="utf-8") as f:
        f.write(data)


def my_str_to_bool(row, endpoint):
    p_fields = ["dead_or_alive"]
    m_fields = ["goes_for_coalition", "goes_for_reelection", "is_substitute", "changed_from_substitute"]
    if endpoint == "person":
        fields = p_fields
    elif endpoint == "membership":
        fields = m_fields
    for field in fields:
        row[field] = True if row[field] == "TRUE" else False
    return row


def make_table(header, dataset):
    table = ','.join(header) + '\n'
    for row_data in dataset:
        for field in header:
            table += f"{row_data[field]},"
        table += '\n'
    return table


def get_contest_id(data, current_chamber, contest_chambers):
    if current_chamber == "gubernatura":
        location = data["state"].lower()
    elif current_chamber == "presidencia":
        location = data["area"].lower()
    elif current_chamber == "diputación":
        location = f"distrito federal {data['city']} de {data['state'].lower()}"
    for i, contest_chamber in enumerate(contest_chambers, start=1):
        if location in contest_chamber and current_chamber in contest_chamber:
            return i


def get_role_name(chamber):
    if chamber == "gubernaturas":
        return "governmentOfficer"
    elif chamber == "alcaldías":
        return "executiveCouncil"
    else:
        return "legislatorLowerBody"


def get_contest_name(chamber):
    if chamber == "gubernaturas":
        return "gubernatura"
    elif chamber == "alcaldías":
        return "presidencia"
    else:
        return "diputación"


def make_person_struct(dataset, chamber, contest_chambers, header):
    people = []
    contest_chamber = get_contest_name(chamber)
    for data in dataset:
        row = dict()
        for field in header:
            if field == "gender":
                row[field] = 2 if data[field] == "F" else 1
            elif field == "dead_or_alive":
                row[field] = True if data[field] == "Vivo" else False
            elif field == "last_degree_of_studies":
                last_degree = data[field].upper()
                row[field] = Catalogues.DEGREES_OF_STUDIES.index(last_degree)
            elif field == "contest_id":
                row[field] = get_contest_id(data, contest_chamber,
                                            contest_chambers)
            else:
                row[field] = data[field]
        people.append(row)
    return people


def make_other_names_struct(dataset, persons_count):
    result = []
    for i, data in enumerate(dataset, start=1):
        # TODO: check multinickname case
        if data["nickname"]:
            result.append({"other_name_type": 2,
                           "name": data["nickname"],
                           "person_id": i + persons_count})
    return result


def make_person_profession(dataset, professions, persons_count):
    lines = []
    pattern = '^profession_[2-6]$'
    for i, data in enumerate(dataset, start=1):
        for field in data:
            if re.search(pattern, field):
                profession = data[field].lower()
                if profession:
                    profession_id = professions.index(profession) + 1
                    lines.append({
                        "person_id": i + persons_count,
                        "profession_id": profession_id
                    })
    return lines


def make_membership(dataset, chamber, parties, coalitions, contest_chambers,
                    header, persons_count):
    lines = []
    contest_chamber = get_contest_name(chamber)
    current_role = get_role_name(chamber)
    for i, data in enumerate(dataset, start=1):
        if data["coalition"]:
            coalition_id = coalitions.index(data["coalition"].lower().strip()) + 1
        else:
            coalition_id = ''
        lines.append({
            "person_id": i + persons_count,
            "role_id": Catalogues.ROLE_TYPES.index(current_role),
            "party_id": parties.index(data["abbreviation"].lower()) + 1,
            "coalition_id": coalition_id,
            "contest_id": get_contest_id(data, contest_chamber,
                                         contest_chambers),
            "goes_for_coalition": True if data["coalition"] else False,
            "membership_type": Catalogues.MEMBERSHIP_TYPES.index(data["membership_type"]),
            "goes_for_reelection": False, # Always false
            "start_date": data["start_date"], "end_date": data["end_date"],
            "is_substitute": True if data["is_substitute"] == "Sí" else False,
            "parent_membership_id": i if data["is_substitute"] == "Sí" else '',
            "changed_from_substitute": False, # TODO:
            "date_changed_from_substitute": "" # TODO:
        })
    return lines


def get_row_urls(row):
    pattern = '(^Website$|^URL_(\w)*$)'
    return {field: row[field] for field in row if re.search(pattern, field) and field != "URL_others"}


def get_url_type_id(field, url_types, url=""):
    email_pattern = '^[\w.+-]+@[\w-]+\.[\w.-]+$'
    if field == "URL_others":
        for u_type in url_types:
            if u_type.lower() in url:
                return url_types.index(u_type) + 1
            elif re.search(email_pattern, url):
                return url_types.index("EMAIL") + 1
        return 0
    else:
        return url_types.index(Catalogues.URL_TYPES[field]) + 1


def make_url_struct(dataset, url_types, current_chamber, persons_count):
    lines = []
    field_pattern = '(^Website$|^URL_(\w)*$)'

    for i, data in enumerate(dataset, start=1):
        for field in data:
            if re.search(field_pattern, field) and field != "URL_others":
                if data[field]:
                    for url in data[field].split(','):
                        row = {
                                "url": data[field],
                                "url_type": get_url_type_id(field, url_types),
                                "description": '', # TODO
                                "owner_type": 4 if field == "source_of_truth" else 1, # TODO: persona, partido, coalicion
                                "owner_id": i + persons_count
                            }
                        lines.append(row)
            elif field == "URL_others":
                for url in data[field].split(","):
                    clean_url = url.strip()
                    if clean_url:
                        row = {
                            "url": clean_url,
                            "url_type": get_url_type_id(field, url_types, url),
                            "description": '', # TODO
                            "owner_type": 1, # TODO: persona, partido, coalicion
                            "owner_id": i + persons_count
                        }
                        lines.append(row)
    return lines


def colors_to_list(data):
    for row in data:
        colors_list = row["colors"].split(",")
        row["colors"] = [color.strip("' ") for color in colors_list]
    return data


def send_data(base_url, endpoint, dataset):
    full_url = base_url + endpoint
    with progressbar.ProgressBar(max_value=len(dataset)) as bar:
        for i, row in enumerate(dataset, start=2):
            try:
                # Sending row data to api
                r = requests.post(full_url, json=row)
            except r_excepts.ConnectionError:
                print("[CONNECTION ERROR]")
                print(f"#{i} | url: {full_url} | data:{row}")
            response = r.json()
            if not response["success"]:
                print(f"[ERROR]: {endpoint} #{i} {r.json()['error']}")
            bar.update(i - 2)
