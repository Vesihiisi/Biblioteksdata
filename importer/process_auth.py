#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Import new Libris authorities to Wikidata.

Tool for mass import of new Libris authority
posts to Wikidata within the Library Data 2018
project.

This is the first version. It only adds Libris URI
to a single post, using either local or online data
(via a provided URI).
"""
import argparse
import json
import os
import pywikibot
import requests

import importer_utils as utils
from Person import Person
from Uploader import Uploader

EDIT_SUMMARY = "#WMSE #LibraryData_KB"
MAPPINGS = "mappings"


def load_mapping_files():
    """Load local and remote mapping files."""
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
    """Check whether it's a person post."""
    return auth_item["@graph"][1]["@type"] == "Person"


def get_from_uri(uri):
    """Load data from uri."""
    url = "https://libris.kb.se/{}/data.jsonld".format(uri)
    return json.loads(requests.get(url).text)


def list_available_files(path, limit=None, uri=None):
    """
    Load a list of files in directory.

    :param limit: return the first x files."
    """
    files = []
    for fname in os.listdir(path):
        files.append(os.path.join(path, fname))
        if uri:
            data = utils.load_json(os.path.join(path, fname))
            file_uri = data["@graph"][0]["@id"].split("/")[-1]
            if file_uri == uri:
                print("Ready to process file with URI {}.".format(uri))
                return [os.path.join(path, fname)]
    if limit:
        files = files[:limit]
    print("Ready to process {} files.".format(len(files)))
    return files


def main(arguments):
    """Get arguments and process data."""
    libris_files = list_available_files(arguments.get("dir"),
                                        arguments.get("limit"),
                                        arguments.get("uri"))

    wikidata_site = utils.create_site_instance("wikidata", "wikidata")
    data_files = load_mapping_files()
    existing_people = utils.get_wd_items_using_prop(
        data_files["properties"]["libris_uri"])

    for fname in libris_files:
        data = utils.load_json(fname)
        if is_person(data):
            person = Person(data, wikidata_site, data_files, existing_people)
            if arguments.get("upload"):
                live = True if arguments["upload"] == "live" else False
                uploader = Uploader(person, repo=wikidata_site,
                                    live=live, edit_summary=EDIT_SUMMARY)
                try:
                    uploader.upload()
                except pywikibot.data.api.APIError as e:
                    print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    parser.add_argument("--uri")
    parser.add_argument("--upload", action='store')
    parser.add_argument("--limit",
                        nargs='?',
                        type=int,
                        action='store')
    args = parser.parse_args()
    main(vars(args))
