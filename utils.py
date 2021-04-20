import re
from validations import (last_name_check, membership_type_check,
                         date_format_check, url_check, profession_check,
                         url_other_check)


class Catalogues:
    DEGREES_OF_STUDIES = ['', 'ELEMENTARY', 'HIGH SCHOOL', 'ASSOCIATE DEGREE',
                          'BACHELOR’S DEGREE',
                          'UNIVERSITY 1ST PROFESSIONAL DEGREE',
                          'MASTER DEGREE', 'PHD DEGREE']
    #   GOBERNADOR, DIPUTADO , PRESIDENTE MUNICIPAL
    DISTRICT_TYPES = ['NATIONAL_EXEC', 'REGIONAL_EXEC', 'NATIONAL_LOWER', 'LOCAL_EXEC']
    GENDERS = ['', 'M', 'F']
    MEMBERSHIP_TYPES = ['', 'officeholder', 'campaigning_politician', 'party_leader']
    # privilegiado, apodo, nombre de la boleta
    OTHER_NAMES_TYPES = ['', 'preferred', 'nickname', 'ballot_name']
    #   GOBERNADOR, DIPUTADO , PRESIDENTE MUNICIPAL
    ROLE_TYPES = ['', 'governmentOfficer', 'legislatorLowerBody', 'executiveCouncil']
    URL_TYPE_NAMES = ['',
                      'campaign', 'official', 'personal', 'wikipedia',
                      'campaign', 'official', 'personal',
                      'campaign', 'official', 'personal',
                      'WhatsApp', 'Twitter', 'YouTube', 'LinkedIn', 'Flickr',
                      'Pinterest', 'Tumblr', 'RSS', ]


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
        print(f"Checking row #{i} = {row[3]}")
        line = f'{i}'
        # Change row from list to dict with relevant information (test fields)
        data = row_to_dict(row, header)
        # Tests suite start
        line += ",last_name" if not last_name_check(data["last_name"] or []) else ""
        line += ",membership_type" if not membership_type_check(data["membership_type"]) else ""
        line += ",start_date" if not date_format_check(data["start_date"]) else ""
        line += ",end_date" if not date_format_check(data["end_date"]) else ""
        line += ",date_birth" if not date_format_check(data["date_birth"]) else ""
        professions = get_columns_data(data, "profession")
        # TODO: from 2 to 6 only
        line += ",professions" if not profession_check(professions.values()) else ""
        line += ",Website" if not url_check(data["Website"], "light") else ""
        line += ",URL_FB_page" if not url_check(data["URL_FB_page"], "strict") else ""
        line += ",URL_FB_profile" if not url_check(data["URL_FB_profile"], "strict") else ""
        line += ",URL_IG" if not url_check(data["URL_IG"], "strict") else ""
        line += ",URL_TW" if not url_check(data["URL_TW"], "strict") else ""
        url_others = data["URL_others"].split(",")
        line += url_other_check(url_others)
        # If no errors, discard this line
        if line == str(i):
            line = ''
            continue
        # Adding candidate name at the end of the line
        else:
            line += f",{row[3]}"
            lines.append(line)
    return lines


def write_report(data, name):
    """**Write a report with the errors found  at the sheet**

    :param data: A comma separated string with line number and fields with errors
    :type data: str
    """
    with open(f"{name}.csv", 'w', encoding="utf-8") as f:
        f.write(data)


def my_str_to_bool(row, endpoint):
    """
    docstring
    """
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


def get_contest_id(state, current_chamber, contest_chambers):
    state = state.lower()
    current_chamber = current_chamber.lower()
    for i, contest_chamber in enumerate(contest_chambers, start=1):
        contest_chamber = contest_chamber[0].lower()
        if state in contest_chamber and current_chamber in contest_chamber:
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
    contest = get_contest_name(chamber)
    for data in dataset:
        row = dict()
        for field in header:
            if field == "gender":
                row[field] = 2 if data[field] == "F" else 1
            elif field == "dead_or_alive":
                row[field] = True if data[field] == "Vivo" else False
            elif field == "last_degree_of_studies":
                row[field] = Catalogues.DEGREES_OF_STUDIES.index(data[field].upper())
            elif field == "contest_id":
                row[field] = get_contest_id(data["state"], contest, contest_chambers)
            else:
                row[field] = data[field]
        people.append(row)
    return people


def make_other_names_struct(dataset):
    row = dict()
    result = []
    for i, data in enumerate(dataset, start=1):
        if data["nickname"]:
            result.append({"other_name_type": 2,
                           "name": data["nickname"],
                           "person_id": i})
    return result


def make_person_profession(dataset, professions):
    # Professions is a list of lists. Getting proferssion string
    professions = [p[0].lower() for p in professions]
    lines = []
    for i, data in enumerate(dataset, start=1):
        current_professions = get_columns_data(data, "profession")
        for p_id in range(2, 7):
            current_profession = data[f"profession_{p_id}"].lower()
            if current_profession in professions:
                lines.append({"person_id": i,
                              "profession_id": professions.index(current_profession) + 1})
    return lines


def make_membership(dataset, chamber, parties, coalitions, contest_chambers, header):
    """TODO: Docstring for make_membership.
    :returns: TODO

    """
    lines = []
    # Parties is a list of lists. Getting party string
    parties = [p[0].lower() for p in parties]
    coalitions = [c[0].lower().strip() for c in coalitions]
    contest = get_contest_name(chamber)
    current_role = get_role_name(chamber)
    for i, data in enumerate(dataset, start=1):
        if data["coalition"]:
            coalition_id = coalitions.index(data["coalition"].lower().strip()) + 1
        else:
            coalition_id = ''
        lines.append({
            "person_id": i,
            "role_id": Catalogues.ROLE_TYPES.index(current_role),
            "party_id": parties.index(data["abbreviation"].lower()),
            "coalition_id": coalition_id,
            "contest_id": get_contest_id(data["state"], contest, contest_chambers),
            "goes_for_coalition": True if data["coalition"] else False,
            "membership_type": Catalogues.MEMBERSHIP_TYPES.index(data["membership_type"]),
            "goes_for_reelection": False, # Always false
            "start_date": data["start_date"], "end_date": data["end_date"],
            "is_substitute": True if data["is_substitute"] == "Sí" else False,
            "parent_membership_id": i if data["is_substitute"] == "Sí" else '',
            "changed_from_substitute": False, # TODO
            "date_changed_from_substitute": "" # TODO
        })
    return lines

def get_row_urls(row):
    """TODO: Docstring for get_row_urls.
    :returns: TODO

    """
    pattern = '(^Website$|^URL_(\w)*$)'
    return {field: row[field] for field in row if re.search(pattern, field) and field != "URL_others"}


def get_url_type_id(field, url_types):
    if field == "Website":
        return url_types.index("WEBSITE_OFFICIAL") + 1
    elif field == "URL_FB_page":
        return url_types.index("FACEBOOK_CAMPAIGN") + 1
    elif field == "URL_FB_profile":
        return url_types.index("FACEBOOK_PERSONAL") + 1
    elif field == "URL_IG":
        return url_types.index("INSTAGRAM_CAMPAIGN") + 1
    elif field == "URL_TW":
        return url_types.index("TWITTER") + 1
    else:
        return ''


def make_url_struct(dataset, url_types):
    """TODO: Docstring for make_url_struct.

    :arg1: TODO
    :returns: TODO

    """
    lines = []
    url_types = [u[0] for u in url_types]
    for i, data in enumerate(dataset, start=1):
        current_urls = get_row_urls(data)
        row = dict()
        for field in current_urls:
            if data[field]:
                lines.append({"url": data[field],
                            "url_type": get_url_type_id(field, url_types),
                            "description": '', # TODO
                            "owner_type": 1, # TODO: depende de la hoja que este leyendo
                            "owner_id": i
                            })
    return lines

