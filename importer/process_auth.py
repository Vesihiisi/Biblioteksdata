#!/usr/bin/python
# -*- coding: utf-8  -*-
import argparse
import json
import requests


def get_nationality(auth_item):
    """http://www.loc.gov/marc/geoareas/introduction.pdf"""
    nat = auth_item["@graph"][1]["nationality"][0]["@id"].split("/")[-1]
    return nat


def get_occupation(auth_item):
    bio_section = auth_item["@graph"][1]
    if bio_section.get("hasOccupation"):
        occs = bio_section.get("hasOccupation")[0].get("label")
        return [x.lower() for x in occs]


def get_dates(auth_item):
    dates = {"born": None, "dead": None}
    bio_section = auth_item["@graph"][1]
    life = bio_section["lifeSpan"].split("-")
    if len(life[0]) == 4:
        dates["born"] = life[0]
    if len(life[1]) == 4:
        dates["dead"] = life[1]
    if "birthDate" in bio_section.keys():
        dates["born"] = bio_section["birthDate"]
    if "deathDate" in bio_section.keys():
        dates["dead"] = bio_section["deathDate"]
    return dates


def get_descriptions(auth_item):
    descs = []
    bio_info = auth_item["@graph"][1]["hasBiographicalInformation"]
    for el in bio_info:
        if el["@type"] == "BiographicalNote":
            descs.append(el["label"])
    return descs


def is_person(auth_item):
    return auth_item["@graph"][1]["@type"] == "Person"


def get_first_name(auth_item):
    return auth_item["@graph"][1]["givenName"]


def get_surname(auth_item):
    return auth_item["@graph"][1]["familyName"]


def get_uri(auth_item):
    return auth_item["@graph"][0]["@id"].split("/")[-1]


def get_selibr(auth_item):
    return auth_item["@graph"][0]["controlNumber"]


def get_ids(auth_item):
    allowed_types = ["viaf", "isni"]
    auth_ids = []
    bio_section = auth_item["@graph"][1]
    if bio_section.get("identifiedBy"):
        for i in bio_section.get("identifiedBy"):
            if i["@type"] == "Identifier" and i["typeNote"] in allowed_types:
                auth_ids.append({"type": i["typeNote"], "value": i["value"]})
    return auth_ids


def get_from_uri(uri):
    url = "https://libris-qa.kb.se/{}/data.jsonld".format(uri)
    return json.loads(requests.get(url).text)


def get_data(args):
    if args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
    elif args.uri:
        data = get_from_uri(args.uri)
    return data


def main(data):
    print(is_person(data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--uri")
    args = parser.parse_args()
    data = get_data(args)
    main(data)
