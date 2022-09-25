# import skolenhetsregister as sker
import requests
import json
from tqdm import tqdm
from bs4 import BeautifulSoup

# Url parameters
# Search type: sok={SokA, SokB, SokC, SokD}

# sokA:
# Skolform: vfrom={integer} - Grundskola:11
# flik=s


# Kommun or huvudman. OBLIGATORY
# Huvudman: hman={id, or empty for all} and hmtyp=F
# Kommun: kommun={id, or empty for all} and hmtyp=undefined

# Skola
# no parameter or: one={school id}

# If you can choose year: ar={year or senaste}

# CASE 1, let's understand how to scrape the grades for a specific search:
# kommun: Stockholm - 0180, lankod = 01
# all schools
# year: latest
# grade: 6
# parent_url = "https://www.skolverket.se/skolutveckling/statistik/sok-statistik-om-forskola-skola-och-vuxenutbildning?sok=SokA&hmtyp=undefined&flik=s&vform=11&kommun=0180&ar=senaste&run=1"


def get_national_test_results_by_year_and_kommun(
    kommun_code, search_year, operation_year, grade, school_form
):
    search_year = "senaste"

    url = "https://siris.skolverket.se/reports/rwservlet?cmdkey=common&geo=1"

    if grade == "6":
        url += "&report=gr_prov_ak6"
    else:
        url += "&report=gr_prov_ak9"

    url += f"&p_verksamhetsar={operation_year}"
    url += f"&p_kommunkod={kommun_code}"

    url += "&p_skolkod=&p_hmantyp=&p_hmankod=&p_flik=G"

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    results_container = soup.find_all("table")[1]

    results_rows = [
        row for row in results_container.find_all("tr") if "valign" in row.attrs
    ]  # ignore row-spacers

    results = {
        "kommunkod": kommun_code,
        "school_form": school_form,
        "year": operation_year,
        "grade": grade,
        "national_test_results": {},
    }
    for ind, row in enumerate(results_rows):
        for col in row.find_all("td"):
            if "width" in col.attrs:
                if col["width"] == "755":
                    test_results = results_rows[ind + 1]
                    result_columns = [
                        result
                        for result in test_results.find_all("td")
                        if "width" in result.attrs
                    ]
                    subject_results = {}
                    try:
                        subject_results["boys_average"] = float(
                            result_columns[-1].text.replace(",", ".")
                        )
                        subject_results["girls_average"] = float(
                            result_columns[-2].text.replace(",", ".")
                        )
                        subject_results["total_average"] = float(
                            result_columns[-3].text.replace(",", ".")
                        )
                    except ValueError:  # results don't exist, just move on.
                        pass
                    results["national_test_results"][col.text] = subject_results

    return results


# ----TEST----
# stockholms_kommun_results = get_national_test_results_by_year_and_kommun(
#     "0180", "senaste", "2019", "6", "11"
# )
# print(stockholms_kommun_results)


# Go through all kommuns.
# We need a list of available kommun codes.
def get_national_tests_results_by_year(kommun_codes, grade, year, school_form):
    all_national_test_results_in_year = []
    for code_entry in tqdm(kommun_codes):
        code = code_entry["Kommunkod"]
        kommun_national_test_results = get_national_test_results_by_year_and_kommun(
            code, "senaste", year, grade, school_form
        )
        all_national_test_results_in_year.append(kommun_national_test_results)

    return all_national_test_results_in_year


with open("kommunkoder.json", "r") as f:
    kommun_codes = json.load(f)

data = []
for grade in tqdm(["6", "9"]):
    for year in tqdm(
        ["2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010"]
    ):
        # for school_form in tqdm(["11", "21"]):
        kommun_national_test_results = get_national_tests_results_by_year(
            kommun_codes, grade, year, "11"
        )
        data += kommun_national_test_results

with open(f"national_test_results_grundskola2.json", "w") as f:
    json.dump(data, f, indent=4)
