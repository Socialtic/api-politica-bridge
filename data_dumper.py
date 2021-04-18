import requests
from requests import exceptions as r_excepts
from utils import row_to_dict, make_banner, my_str_to_bool
from sheets_reader import get_sheets_data

STRUCT_SHEET_ID = "1fKXpwXhKlLLG-kjh8udQIH9poNLs7kAzSnXndZ1Le4Y"
READ_RANGES = ["Table area!B1:H2640", "Table chamber!B1:C357",
               "Table role!B1:F357", "Table coalition!B1:D31",
               "Table party!B1:F78", "Table person!B1:I114",
               "Table other-name!B1:D17", "Catalogue profession!B1:B120",
               "Table person-profession!B1:C268",
               # "Table past_membership!A1:G1",
               "Table membership!B1:O114", "Table contest!B1:G357",
               "Table url!B1:F315"]
API_BASE = 'http://localhost:5000/'


def main():
    for read_range in READ_RANGES:
        sheet = get_sheets_data(STRUCT_SHEET_ID, read_range)
        # Getting header
        header = sheet.pop(0)
        dataset = [row_to_dict(row, header) for row in sheet]
        endpoint = read_range.split("!")[0].split(" ")[1]
        full_url = API_BASE + endpoint
        make_banner(f"UPLOAD TO {endpoint}")
        for i, row in enumerate(dataset, start=2):
            if endpoint in ["person", "membership"]:
                row = my_str_to_bool(row, endpoint)
            try:
                # Sending row data to api
                r = requests.post(full_url, json=row)
            except r_excepts.ConnectionError:
                print("[CONNECTION ERROR]")
                print(f"#{i} | url: {full_url}")
            response = r.json()
            if not response["success"]:
                print("#", i, r.json())


if __name__ == "__main__":
    main()
