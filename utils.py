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
    m_fields = ["goes_for_coalition", "goes_for_reelection", "is_substitute", "changed_from_sustitute"]
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


def make_person_struct(dataset, chamber, contest_chambers, header):
    people = []
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
                row[field] = get_contest_id(data["state"], chamber, contest_chambers)
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
    pass
