#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Generate list of most common books and authors.

This takes a tsv file in the format ISBN : count
and uses the Libris API to resolve
the ISBN's to titles and authors.
"""
import argparse
import csv
import json
import requests

import importer_utils as utils
from Work import Work

URL = "http://api.libris.kb.se/xsearch?query=ISBN:{}&format=json"
OUTPUT = "isbn_output.tsv"
OUTPUT_AUTHORS = "authors_output.tsv"
LIBRIS = "P1182"
ISBN13 = "P212"
ISBN10 = "P957"


def get_existing_works():
    """Get WD items that use identifiers."""
    libris_works = utils.get_wd_items_using_prop(LIBRIS)
    isbn13_works = utils.get_wd_items_using_prop(ISBN13)
    isbn10_works = utils.get_wd_items_using_prop(ISBN10)
    return {"libris": libris_works,
            "isbn13": isbn13_works,
            "isbn10": isbn10_works}


def load_frequencies(fname):
    """Load the ISBN frequency file."""
    frequencies = []
    with open(fname) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if "/" not in row[0] and "." not in row[0]:
                book = {}
                book["id"] = row[0]
                book["count"] = row[1]
                frequencies.append(book)
    return frequencies


def download_data(isbn):
    """
    Download data about an ISBN.

    Search for an ISBN in the API
    and return all the matching records.
    """
    book_url = URL.format(isbn)
    book_data = json.loads(requests.get(book_url).text)
    records = book_data["xsearch"]["records"]
    if records > 0:
        return book_data["xsearch"]["list"]
    else:
        return False


def save_authors_list(authors):
    """Save the list of authors + occurrence counts."""
    with open(OUTPUT_AUTHORS, 'w') as output_file:
        csvwriter = csv.writer(output_file, delimiter='\t')
        csvwriter.writerow(["count", "name"])
        for person in authors:
            values = authors[person]
            to_print = [values["count"], values["name"]]
            csvwriter.writerow(to_print)


def save_works_list(works):
    """
    Save the works list to file.

    Only save selected parts of the Libris post.
    """
    with open(OUTPUT, 'w') as output_file:
        csvwriter = csv.writer(output_file, delimiter='\t')
        csvwriter.writerow(["count", "isbn", "wikidata", "author",
                            "title", "LIBRIS", "language"])
        for item in works:
            values = works[item]
            to_print = [values.count, values.searched_isbn,
                        values.wikidata, values.creator, values.title,
                        values.libris, values.language]
            csvwriter.writerow(to_print)


def main(args):
    """Process ISBN:count list from provided file."""
    works = {}
    authors = {}
    existing_works = get_existing_works()
    frequencies = load_frequencies(args.path)
    for item in frequencies[:args.limit]:
        isbn = item["id"]
        work = Work()
        work.searched_isbn = item["id"]
        records = download_data(isbn)
        if records and len(records) == 1:
            for record in records:
                work.load_libris_data(record)
                work.count = item["count"]
                if work.creator:
                    if work.creator not in authors.keys():
                        authors[work.creator] = {"name": work.creator,
                                                 "count": int(item["count"])}
                    else:
                        authors[work.creator]["count"] += int(item["count"])
        work.count = item["count"]
        work.add_wikidata(existing_works)
        works[isbn] = work
    save_works_list(works)
    save_authors_list(authors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    main(args)
