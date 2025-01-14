import requests
from collections import defaultdict
import sys
import json
from jinja2 import Template
import datetime

DATA_FILE = "data.json"
COUNCILLOR_DATA_FILE = "councillors.json"
URL = "http://mapit.code4sa.org/address?address=%s&generation=2&type=WD"
URLxy = "http://mapit.code4sa.org/point/4326/%s,%s"

def get_age(idnumber):
    year = 1900 + int(idnumber[0:2])
    month = int(idnumber[2:4])
    day = int(idnumber[4:6])
    today = datetime.datetime.now()
    birthday = datetime.datetime(year=year, month=month, day=day)
    age = (today - birthday).days / 365
    return age


def load_data():
    ids = defaultdict(list)
    data = json.load(open(DATA_FILE))
    councillor_data = json.load(open(COUNCILLOR_DATA_FILE))
    for ward, candidates in data.items():
        for candidate in candidates:
            idno = candidate["IDNumber"]
            ids[idno].append(ward)
    return data, ids, councillor_data

def coords_to_ward(lon, lat):
    url = URLxy % (lon, lat)
    r = requests.get(url)
    js = r.json()
    ward_no = None

    for key in js:
        if js[key]["type_name"] == 'Ward':
            ward_no = js[key]["name"]
            ward_no = js[key]["name"]

    return {
        "ward": ward_no,
        "address": 'Used geolocation data for Latitude: %.4f and Longitude: %.4f' % (float(lat), float(lon))
    }

def ward_to_ward(ward_no):
    return {
        "ward": ward_no,
        "address": "Ward: %s" % ward_no
    }

def address_to_ward(address):
    r = requests.get(URL % address)
    js = r.json()
    ward_no = None
    formatted_address = "Unknown"

    for key in js:
        if "type_name" in js[key]:
            ward_no = js[key]["name"]
            ward_key = key

    for address in js["addresses"]:
        if ward_key in address["areas"]:
            formatted_address = address["formatted_address"]
    return {
        "ward" : ward_no,
        "address" : formatted_address
    }

def get_candidates(ward):
    return data.get(ward, None)

def get_proportional_representation(ward, result):
    councillor = councillor_data.get(ward, None)

    if councillor:
        result["councillor"] = councillor
        result["proportional representation"] =  councillor_data.get(councillor[0]["Municipality"], None)
        return result

    # In case ward has no councillor yet...
    candidates = data.get(ward, None)
    if candidates :
        print candidates[0]
        print candidates[0].get("Municipality")
        result["proportional representation"] =  councillor_data.get(candidates[0].get("Municipality"), [])
        return result

    return result
data, ids, councillor_data = load_data()

if __name__ == "__main__":
    address = raw_input("Enter in your address: ")
    ward = address_to_ward(address)

    template = Template(open("index.html").read())
    print template.render(candidates=data[ward])
