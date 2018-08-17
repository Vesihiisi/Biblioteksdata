#!/usr/bin/python
# -*- coding: utf-8  -*-
import argparse
import json
import os
import pywikibot
import requests

import importer_utils as utils
from Person import Person
from Uploader import Uploader

EDIT_SUMMARY = "test"
MAPPINGS = "mappings"


def load_mapping_files():
    mappings = {}
    local = ["properties", "countries", "professions"]
    remote = ["selibr"]
    for title in local:
        f = os.path.join(MAPPINGS, '{}.json'.format(title))
        mappings[title] = utils.load_json(f)
    for title in remote:
        mappings[title] = utils.get_wd_items_using_prop(
            mappings["properties"][title])
    print("Loaded local mappings: {}.".format(", ".join(local)))
    print("Loaded remote mappings: {}.".format(", ".join(remote)))
    return mappings


def is_person(auth_item):
    return auth_item["@graph"][1]["@type"] == "Person"


def get_from_uri(uri):
    url = "https://libris-qa.kb.se/{}/data.jsonld".format(uri)
    return json.loads(requests.get(url).text)


def get_data(args):
    if args.get("file"):
        with open(args.get("file"), 'r') as f:
            data = json.load(f)
    elif args.get("uri"):
        data = get_from_uri(args.get("uri"))
    return data


def main(arguments):
    data = get_data(arguments)
    wikidata_site = utils.create_site_instance("wikidata", "wikidata")
    data_files = load_mapping_files()
    existing_people = utils.get_wd_items_using_prop(
        data_files["properties"]["libris_uri"])
    if is_person(data):
        person = Person(data, wikidata_site, data_files, existing_people)
        if arguments.get("upload"):
            live = True if arguments["upload"] == "live" else False
            uploader = Uploader(person, repo=wikidata_site,
                                live=live, edit_summary=EDIT_SUMMARY)
            try:
                uploader.upload()
            except pywikibot.data.api.APIError:
                print("fuck you")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--uri")
    parser.add_argument("--upload", action='store')
    args = parser.parse_args()
    main(vars(args))
