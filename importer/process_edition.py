#!/usr/bin/python
# -*- coding: utf-8  -*-
import argparse
import json
import os
import pywikibot
import requests
from stdnum import isbn as isbn_tool
import importer_utils as utils


from Edition import Edition
from Uploader import Uploader

MAPPINGS = "mappings"
EDIT_SUMMARY = "#WMSE #LibraryData_KB"


def get_libris_id(data):
    same_as = data["@graph"][0].get("sameAs")
    if not same_as:
        return
    for sa in same_as:
        if sa["@id"].startswith("http://libris.kb.se/bib/"):
            return sa["@id"].split("/")[-1]


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


def normalize_isbn_map(data):
    normalized = {}
    for k, v in data.items():
        if isbn_tool.is_valid(k):
            compact_isbn = isbn_tool.compact(k)
            normalized[compact_isbn] = v
    return normalized


def load_mapping_files():
    """Load local and remote mapping files."""
    mappings = {}
    local = ["properties", "languages",
             "places", "publishers"]
    remote = ["isbn_10", "isbn_13", "libris_edition"]
    for title in local:
        f = os.path.join(MAPPINGS, '{}.json'.format(title))
        mappings[title] = utils.load_json(f)
    for title in remote:
        data = utils.get_wd_items_using_prop(
            mappings["properties"][title])
        if title in ["isbn_10", "isbn_13"]:
            data = normalize_isbn_map(data)
        mappings[title] = data
    print("Loaded local mappings: {}.".format(", ".join(local)))
    print("Loaded remote mappings: {}.".format(", ".join(remote)))
    return mappings


def get_from_uri(uri):
    """Load data from uri."""
    url = "https://libris.kb.se/{}/data.jsonld".format(uri)
    return json.loads(requests.get(url).text)


def get_lines_from_file(filepath):
    with open(filepath) as f:
        content = f.readlines()
    return [x.strip() for x in content]


def main(arguments):
    wikidata_site = utils.create_site_instance("wikidata", "wikidata")
    data_files = load_mapping_files()
    cache = {}
    existing_editions = utils.get_wd_items_using_prop(
        data_files["properties"]["libris_uri"])
    if arguments.get("uri"):
        mode = "uri"
        data = get_from_uri(arguments.get("uri"))
        edition = Edition(data, wikidata_site, data_files,
                          existing_editions, cache, mode)
        problem_report = edition.get_report()
        if arguments.get("upload"):
            live = True if arguments["upload"] == "live" else False
            uploader = Uploader(edition, repo=wikidata_site,
                                live=live, edit_summary=EDIT_SUMMARY)
            if "Q" in problem_report and problem_report["Q"] == "":
                problem_report["Q"] = uploader.wd_item_q
            try:
                uploader.upload()
            except pywikibot.data.api.APIError as e:
                print(e)
    elif arguments.get("dir") and arguments.get("libris_list"):
        mode = "local"
        available_files = list_available_files(arguments.get("dir"))
        libris_list = get_lines_from_file(arguments["libris_list"])
        for fname in available_files:
            data = utils.load_json(fname)
            selibr = get_libris_id(data)
            if selibr and selibr in libris_list:
                edition = Edition(data, wikidata_site, data_files,
                                  existing_editions, cache, mode)
                problem_report = edition.get_report()
                if arguments.get("upload"):
                    live = True if arguments["upload"] == "live" else False
                    uploader = Uploader(edition, repo=wikidata_site,
                                        live=live, edit_summary=EDIT_SUMMARY)
                    if "Q" in problem_report and problem_report["Q"] == "":
                        problem_report["Q"] = uploader.wd_item_q
                    try:
                        uploader.upload()
                    except pywikibot.data.api.APIError as e:
                        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir")
    parser.add_argument("--uri")
    parser.add_argument("--libris_list")
    parser.add_argument("--upload", action='store')
    parser.add_argument("--limit",
                        nargs='?',
                        type=int,
                        action='store')
    args = parser.parse_args()
    main(vars(args))
