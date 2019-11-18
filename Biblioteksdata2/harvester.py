#!/usr/bin/python
# -*- coding: utf-8  -*-
"""Download and pre-process data of Libris editions.

Removes the irrelevant data and simplifies
the relevant parts. The output can be loaded
into OpenRefine for reconciliation and Wikidata
upload.

Usage:
    --book IDENTIFIER process single entry, using either
                      old Edition ID or URI
    --list FILENAME   process a list of ID's (either Edition
                      or URI allowed), one per line
    --out  FILENAME   specify filename to save the output,
                      otherwise default filename will be
                      used
"""
import argparse
import json
import requests

OUTPUT_FILE = "output.json"


def json_to_file(filename, content):
    """
    Pretty write json object to file.

    @param filename: file to save to
    @type filename: string
    @param content: content to save
    @type content: dictionary
    """
    with open(filename, 'w') as fname:
        json.dump(content, fname, indent=4,
                  separators=(',', ': '),
                  sort_keys=True)
        fname.write('\n')
    print("Saved {} objects to {}".format(len(content), filename))


def is_libris_edition_id(identifier):
    """
    Check if identifier is old-format Libris ID.

    @param identifier: ID to check
    @type identifier: string
    """
    if len(identifier) <= 9 and identifier.isdigit():
        return True
    return False


def delistify(some_list):
    """
    Untangle multiple nested one-element lists.

    Occasionally a problem in Libris,
    e.g. "[['x']]". Converts it to 'x'.

    @param some_list: list to convert.
    @type some_list: list
    """
    while isinstance(some_list, list) and len(some_list) == 1:
        some_list = some_list[0]
    return some_list


def file_to_list(some_file):
    """
    Read a text file to a list, row by row.

    @param some_file: path of file to read
    @type some_file: string
    """
    with open(some_file) as fname:
        return fname.read().splitlines()


def get_from_id(identifier):
    """
    Load data from edition id or uri.

    @param identifier: edition identifier (old or URI)
    @type identifier: string
    """
    if is_libris_edition_id(identifier):
        url = "http://libris.kb.se/resource/bib/{}"
    else:
        url = "https://libris.kb.se/{}"
    headers = {'Accept': 'application/json'}
    return json.loads(requests.get(url.format(identifier),
                                   headers=headers).text)


def get_bibliography(raw):
    """
    Get markers of catalogs this books belongs to.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    bibliography = raw.get("bibliography")
    return delistify([x["sigel"]
                      for x in bibliography])


def get_isbn(raw):
    """
    Extract ISBN(s).

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    identified_by = raw["mainEntity"].get("identifiedBy")
    if identified_by:
        isbns = [x for x in identified_by
                 if x["@type"].lower() == "isbn"]
        return [x["value"] for x in isbns][0]
    return None


def get_distribution_format(raw):
    """
    Extract distribution format (hardback, soft etc).

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    identified_by = raw["mainEntity"].get("identifiedBy")
    if identified_by:
        isbns = [x for x in identified_by
                 if x["@type"].lower() == "isbn"]
        if [x.get("qualifier") for x in isbns][0]:
            return delistify([x.get("qualifier") for x in isbns][0])
    return None


def get_title(raw):
    """
    Extract main title.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    title = raw["mainEntity"].get("hasTitle")
    return [x.get("mainTitle") for x in title if
            x["@type"] == "Title"][0]


def get_subtitle(raw):
    """
    Extract subtitle if present.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    title = raw["mainEntity"].get("hasTitle")
    return [x.get("subtitle") for x in title if
            x["@type"] == "Title"][0]


def get_extent(raw):
    """
    Extract number of pages.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    extent = raw["mainEntity"].get("extent")
    extent = [x["label"] for x in extent if
              x["@type"] == "Extent"][0]
    return delistify(extent)


def get_publication_year(raw):
    """
    Extract publication year.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    publication = raw["mainEntity"].get("publication")
    primary = [x for x in publication if
               x["@type"] == "PrimaryPublication"]
    if primary:
        return [x["year"] for x in primary][0]
    return None


def get_publication_place(raw):
    """
    Extract publication place.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    publication = raw["mainEntity"].get("publication")
    primary = [x for x in publication if
               x["@type"] == "PrimaryPublication"]
    if primary:
        place = [x["place"] for x in primary][0]
        return delistify([x["label"] for x in place if
                          x["@type"] == "Place"][0])
    return None


def get_publisher(raw):
    """
    Extract publisher.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    publication = raw["mainEntity"].get("publication")
    primary = [x for x in publication if
               x["@type"] == "PrimaryPublication"]
    if primary:
        return delistify([x["agent"]["label"]
                          for x in primary][0])
    return None


def get_language(raw):
    """
    Extract language of the edition.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    language = raw["mainEntity"]["instanceOf"].get("language")
    if language:
        return [x["code"] for x in language][0]
    return None


def get_contributors(raw):
    """
    Extract contributors.

    Only contributors tagged as belonging
    to any of the valid roles will be extracted.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    valid_roles = ["author", "editor",
                   "translator", "illustrator"]
    agents = {"author": [], "editor": [],
              "translator": [], "illustrator": []}
    contribution = raw["mainEntity"]["instanceOf"].get("contribution")
    for agent in contribution:
        raw_role = agent.get("role")
        if not raw_role:
            ag_role = "author"
        else:
            ag_role = agent["role"][0]["@id"].split("/")[-1]
        if ag_role in valid_roles:
            ag_id = agent["agent"].get("@id") or ""
            ag_first = agent["agent"].get("givenName") or ""
            ag_last = agent["agent"].get("familyName") or ""
            ag_full = "{} {}".format(ag_first, ag_last)
            agents[ag_role].append({"name": ag_full, "id": ag_id})
    return agents


def get_libris_edition(raw):
    """
    Extract old-format Libris ID.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    control_number = raw["controlNumber"]
    if is_libris_edition_id(control_number):
        return control_number
    return None


def get_uri(raw):
    """
    Extract URI of edition.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    return raw["@id"].split("/")[-1]


def get_modified(raw):
    """
    Extract last modification date of Libris post.

    To be used as 'published' date in reference note
    on Wikidata.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    return raw["modified"]


def process_data(raw):
    """
    Simplify JSON object of a Libris edition.

    Gets rid of the data that is not needed
    and simplifies the needed parts.

    @param raw: json object of a Libris edition
    @type raw: dictionary
    """
    clean = {}
    clean["uri"] = get_uri(raw)
    clean["libris_ed"] = get_libris_edition(raw) or ""
    clean["bibliography"] = get_bibliography(raw)
    clean["ISBN"] = get_isbn(raw) or ""
    clean["publisher"] = get_publisher(raw) or ""
    clean["publicationYear"] = get_publication_year(raw) or ""
    clean["publicationPlace"] = get_publication_place(raw) or ""
    clean["distributionFormat"] = get_distribution_format(raw) or ""
    clean["title"] = get_title(raw)
    clean["subtitle"] = get_subtitle(raw) or ""
    clean["extent"] = get_extent(raw) or ""
    clean["contributors"] = get_contributors(raw) or ""
    clean["language"] = get_language(raw) or ""
    clean["modified"] = get_modified(raw)
    return clean


def main(args):
    """Process given arguments."""
    output = []
    if args.get("list"):
        to_process = file_to_list(args.get("list"))
    elif args.get("book"):
        to_process = [args.get("book")]
    if args.get("out"):
        filename = "{}.json".format(args.get("out"))
    else:
        filename = OUTPUT_FILE
    print("Ready to process {} editions.".format(len(to_process)))
    for i, book_id in enumerate(to_process):
        raw_data = get_from_id(book_id)
        output.append(process_data(raw_data))
        print("Processed {}/{}.".format(i + 1, len(to_process)))
    json_to_file(filename, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    arggroup = parser.add_mutually_exclusive_group(required=True)
    arggroup.add_argument("--book", help="process single entry, \
        using either old Edition ID or URI")
    arggroup.add_argument("--list", help="process a list of ID's (either Edition \
                      or URI allowed), one per line")
    parser.add_argument("--out", help="specify filename to save the output, \
                      otherwise default filename will be used")
    args = parser.parse_args()
    main(vars(args))
