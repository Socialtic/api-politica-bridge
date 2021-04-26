import re
import datetime


def last_name_check(lastname):
    """**Check if lastname has at least two items**

    :param lastname: A lastname in list format
    :type: list
    :return: True is pass test, False otherwise
    :rtype: bool
    """
    return True if len(lastname.split(' ')) >= 2 else False


def membership_type_check(membership):
    """**Check if membership type is campaing_politician until June 2**

    :param membership: The membership type
    :type membership: str
    :return: True if membership type is campaing_politician and date is before June 2, False otherwise
    :rtype: bool
    """
    current_date = datetime.datetime.now()
    limit_date = datetime.datetime(2021, 6, 2)
    member_condition = membership == "campaigning_politician"
    date_condition = current_date <= limit_date
    return True if member_condition and date_condition else False


def date_format_check(date):
    """**Check if date has the format YYYY-MM-DD and a valid date**

    :param date: A date
    :type: str
    :return: True if date has the format YYYY-MM-DD with a valid date False
    otherwise
    :rtype: bool
    """
    pattern = '(^(19|20)[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$|^$)'
    return True if re.search(pattern, date) or "" else False


def url_check(url, mode):
    """**Check if the url has the valid format**

    Valid format in regex: "^http[s]?://w{3}\.\w+\.\w+$"

    :param url: A url
    :type: str
    :return: True if the url has a valid format False otherwise
    :rtype: bool
    """

    if mode == "strict":
        pattern = '(^http[s]?:\/\/w{3}\.(facebook|instagram|twitter)\.com\/([\w.%?=-]+)?$|^$)'
    elif mode == "light":
        pattern = '(^http[s]?:\/\/(w{3}\.)?\w+[.\w]+(\/[\w.?%=@&-]+)*$|^$)'
    return True if re.search(pattern, url) else False


def url_other_check(urls):
    wrong_urls = []
    email_pattern = '^[\w.+-]+@[\w-]+\.[\w.-]+$'
    url_pattern = '^http[s]?:\/\/(w{3}\.)?\w+[.\w]+(\/[\w.?%=@&-]+)*$'
    pattern = f'({email_pattern}|{url_pattern}|^$)'
    wrong_urls = [str(i) for i, url in enumerate(urls, start=1) if not re.search(pattern, url.strip())]
    return f",URL_others({','.join(wrong_urls)})" if wrong_urls else ""


def profession_check(professions):
    """**Check if candidate have duplicated professions**

    :param professions: List of professions
    :type professions: list
    :return: True if candidate haven't duplicated professions, False otherwise
    :rtype: bool
    """
    # Ignoting empty columns
    professions = [profession for profession in professions if profession != ""]
    return True if len(professions) == len(set(professions)) else False
