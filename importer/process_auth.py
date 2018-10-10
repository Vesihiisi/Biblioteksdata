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
REPORTING_DIR = "reports"
CACHE = "cache"


def make_filenames(timestamp):
    """Construct the problem and preview filenames."""
    filenames = {}
    utils.create_dir(REPORTING_DIR)
    filenames['reports'] = os.path.join(
        REPORTING_DIR, "report_auth_{}.json".format(timestamp))

    return filenames


def load_mapping_files():
    """Load local and remote mapping files."""
    mappings = {}
    local = ["properties", "countries", "professions",
             "latin_countries", "latin_languages"]
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


def load_caches(keys):
    cache = {}
    for k in keys:
        fpath = os.path.join(CACHE, "{}.json".format(k))
        if os.path.exists(fpath):
            cache[k] = utils.load_json(fpath)
        else:
            cache[k] = {}
    return cache


def dump_caches(wditem_caches):
    for cache in wditem_caches:
        fname = os.path.join(CACHE, "{}.json".format(cache))
        utils.json_to_file(fname, wditem_caches[cache])


def main(arguments):
    """Get arguments and process data."""
    libris_files = list_available_files(arguments.get("dir"),
                                        arguments.get("limit"),
                                        arguments.get("uri"))
    filenames = make_filenames(utils.get_current_timestamp())

    wikidata_site = utils.create_site_instance("wikidata", "wikidata")
    data_files = load_mapping_files()
    existing_people = utils.get_wd_items_using_prop(
        data_files["properties"]["libris_uri"])
    problem_reports = []

    for fname in libris_files:
        data = utils.load_json(fname)
        cache = load_caches(["surname"])
        if is_person(data):
            person = Person(data,
                            wikidata_site,
                            data_files,
                            existing_people,
                            cache)
            dump_caches(person.get_caches())
            problem_report = person.get_report()
            if arguments.get("upload"):
                live = True if arguments["upload"] == "live" else False
                uploader = Uploader(person, repo=wikidata_site,
                                    live=live, edit_summary=EDIT_SUMMARY)
                if "Q" in problem_report and problem_report["Q"] == "":
                    """
                    If the Person didn't have an associated Qid,
                    this means the Uploader has now created a new Item
                    for it -- insert that id into the problem report.
                    """
                    problem_report["Q"] = uploader.wd_item_q
                try:
                    uploader.upload()
                except pywikibot.data.api.APIError as e:
                    print(e)

            if problem_report:
                problem_reports.append(problem_report)
                utils.json_to_file(
                    filenames['reports'], problem_reports, silent=True)
    if problem_reports:
        print("SAVED PROBLEM REPORTS TO {}".format(filenames['reports']))


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
