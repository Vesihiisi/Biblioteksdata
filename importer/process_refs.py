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

URL = "http://api.libris.kb.se/xsearch?query=ISBN:{}&format=json"
OUTPUT = "isbn_output.tsv"
OUTPUT_AUTHORS = "authors_output.tsv"


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
        csvwriter.writerow(["count", "isbn", "author",
                            "title", "LIBRIS", "language"])
        for item in works:
            values = works[item]
            to_print = [values["count"], values["isbn"],
                        values["creator"], values["title"],
                        values["identifier"], values["language"]]
            csvwriter.writerow(to_print)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    works = {}
    authors = {}
    frequencies = load_frequencies(args.path)
    for item in frequencies[:args.limit]:
        isbn = item["id"]
        records = download_data(isbn)
        if records and len(records) == 1:
            for record in records:
                work = record
                work["count"] = item["count"]
                work["isbn"] = item["id"]
                if "creator" not in work.keys():
                    work["creator"] = ""
                else:
                    if work["creator"] not in authors.keys():
                        authors[work["creator"]] = {
                            "name": work["creator"],
                            "count": int(item["count"])}
                    else:
                        authors[work["creator"]]["count"] += int(item["count"])
                work["identifier"] = work["identifier"].split("/")[-1]
        else:
            work = {"identifier": "",
                    "creator": "",
                    "isbn": isbn,
                    "title": "",
                    "language": "",
                    }
        work["count"] = item["count"]
        works[isbn] = work
    save_works_list(works)
    save_authors_list(authors)
