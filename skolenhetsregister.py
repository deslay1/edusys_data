import requests
import json
import sys
from tqdm import tqdm

# Skolenhetsregistret: https://www.scb.se/vara-tjanster/oppna-data/api-for-skolenhetsregistret/
# API spec: http://api.scb.se/UF0109/v2/Help


BASE_URL = "https://api.scb.se/UF0109/v2/"


def get_school_unit(unit_code, date="20220925"):
    r = requests.get(BASE_URL + f"skolenhetsregister/sv/skolenhet/{unit_code}/{date}")
    try:
        school_unit = r.json()["SkolenhetInfo"]
    except KeyError:
        if "finns inte" in json.loads(r.content)["Message"]:
            print("\n" + json.loads(r.content)["Message"])
            return None
        else:
            print(f"\nBAD REQUEST AT SCHOOL UNIT CODE: {unit_code}\n")
            print(r.content)
            # sys.exit()
            return None  # Some don't exist but don't get proper message....so we return anyways
    return school_unit


def get_school_units_for_form(school_form_id):
    r = requests.get(BASE_URL + f"skolenhetsregister/sv/skolform/{school_form_id}")
    school_units = r.json()["Skolenheter"]
    return school_units


def get_school_units():
    # School unit can be either operated by the municipality (public) or by a "huvudman" (private - investment capital board)
    r = requests.get(BASE_URL + "skolenhetsregister/sv/skolenhet")
    school_units = r.json()["Skolenheter"]
    return school_units


def get_school_forms():
    # Available school forms out there, e.g. primary school, middle school...
    r = requests.get(BASE_URL + "skolenhetsregister/sv/skolform")
    print(r.json())
    school_forms = r.json()["Skolformer"]
    return school_forms


def get_kommuns():
    # Kommunkoder
    r = requests.get(BASE_URL + "skolenhetsregister/sv/kommun")
    print(r.json())
    kommuns = r.json()["Kommuner"]
    return kommuns


def get_active_school_units():
    with open("school_units.json", "r") as f:
        data = json.load(f)
    return [x for x in data if x["Status"] == "Aktiv"]


def store_active_school_units(school_units):
    dates = [
        "20210925",
        "20200925",
        "20190925",
        "20180925",
        "20170925",
        "20160925",
        "20150925",
        "20140925",
        "20130925",
        "20120925",
    ]
    for date in tqdm(dates):
        school_unit_info = []
        for unit in tqdm(school_units):
            code = unit["Skolenhetskod"]
            unit_information = get_school_unit(code, date=date)
            if unit_information:
                school_unit_info.append(unit_information)

    with open(f"db_school_units_{date}.json", "w") as f:
        json.dump(school_unit_info, f, indent=4)


if __name__ == "__main__":
    # kommun_codes = get_kommuns()
    # with open("kommunkoder.json", "w") as f:
    #     json.dump(kommun_codes, f, indent=4)

    # school_forms = get_school_forms()
    # with open("school_forms.json", "w") as f:
    #     json.dump(school_forms, f, indent=4)

    # school_units = get_school_units()
    # with open("school_units.json", "w") as f:
    #     json.dump(school_units, f, indent=4)

    # grundskola_id = 5
    # grundskola_units = get_school_units_for_form(grundskola_id)
    # with open("grundskola_units.json", "w") as f:
    #     json.dump(grundskola_units, f, indent=4)

    # gymnasieskola_id = 1
    # gymnasieskola_units = get_school_units_for_form(gymnasieskola_id)
    # with open("gymnasieskola_units.json", "w") as f:
    #     json.dump(gymnasieskola_units, f, indent=4)

    # Now we have a list of all school units
    # We should store information about every unit
    # Only every ACTIVE unit for NOW
    # Every unit has the following good information:
    # 1. unit["Besoksadress]["Adress", "Postnr", "Ort"] - Address
    # 2. unit["Besoksadress]["GeoData"] - Coordinates, we can put the unit on a MAP!!
    # 3. unit["Huvudman"]["Typ"] - Whether it is "Kommun" or not.

    active_school_units = get_active_school_units()
    store_active_school_units(active_school_units)

    # school_unit = get_school_unit(11828295, date="20190925")
    # print(school_unit)
    # with open("school_unit_test.json", "w") as f:
    #     json.dump(school_unit, f, indent=4)
