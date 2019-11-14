#!/usr/bin/python
# -*- coding: utf-8  -*-
"""Download results of API call to Libris xsearch API.

Xsearch query codes:
http://librishelp.libris.kb.se/help/search_codes_swe.jsp

Script follows pagination in the result
and saves the final output to a json file.
"""
import argparse
import json
import requests

BASEURL = "http://libris.kb.se/xsearch?query={}&format=json&n=200&start={}"

SAVEFILE = "xsearch.json"


def permissive_json_loads(text):
    """
    Load json with possible unescaped chars.

    https://stackoverflow.com/a/42208862/12214611

    We encountered some unescaped backslashes
    in the Libris data, which break the
    json parsing. This escapes them
    while reading the text chunk.

    @param text: text to parse as json
    @type text: string
    """
    while True:
        try:
            data = json.loads(text)
        except ValueError as exc:
            if exc.msg == 'Invalid \\escape':
                text = text[:exc.pos] + '\\' + text[exc.pos:]
            else:
                raise
        else:
            return data


def get_from_url(url):
    """
    Retrieve json content from url.

    @param url: url to fetch data from
    @type url: string
    """
    content = requests.get(url).text
    return permissive_json_loads(content)


def json_to_file(filename, content):
    """
    Pretty write json object to file.

    @param filename: file to save to
    @type filename: string
    @param content: content to save
    @type content: dictionary
    """
    with open(filename, 'w') as f:
        json.dump(content, f, indent=4,
                  separators=(',', ': '),
                  sort_keys=True)
        f.write('\n')
    print("Saved {} objects to {}".format(len(content), filename))


def harvest_query(query):
    """
    Harvest results of API call.

    @param query: Libris xsearch query
    @type query: string
    @return API call result as JSON object
    """
    harvest = []
    url = BASEURL.format(query, "1")
    content = get_from_url(url)
    total_hits = content["xsearch"]["records"]
    harvest.extend(content["xsearch"]["list"])
    print("Running query: {}.".format(query))
    print("{} objects to harvest.".format(total_hits))
    print("Harvested: {} objects.".format(len(harvest)))
    while len(harvest) < total_hits:
        to_record = int(content["xsearch"]["to"])
        from_record = to_record + 1
        url = "=".join(url.split("=")[:-1]) + "={}".format(from_record)
        content = get_from_url(url)
        harvest.extend(content["xsearch"]["list"])
        print("Harvested: {} objects.".format(len(harvest)))
    return harvest


def main(args):
    """Read arguments and run API call."""
    if args["file"]:
        filename = "{}.json".format(args["file"])
    else:
        filename = SAVEFILE
    if args["query"]:
        harvest = harvest_query(args["query"])
        json_to_file(filename, harvest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--file")
    args = parser.parse_args()
    main(vars(args))
