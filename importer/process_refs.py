#!/usr/bin/python
# -*- coding: utf-8  -*-
import argparse
import csv
import json
import re
import requests

URL = "http://api.libris.kb.se/xsearch?query=ISBN:{}&format=json"
FILENAME = "isbn_sorted_medium.tsv"


def only_digits(input):
    """
    Remove punctuation from ISBN.

    Some ISBN numbers in Libris have ;
    in them.
    """
    return re.sub('[^\w\s]', '', input)


def load_frequencies(fname):
    """Load the ISBN frequency file."""
    frequencies = {}
    with open(fname) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if "/" not in row[0] and "." not in row[0]:
                book = {}
                book["id"] = row[0]
                book["count"] = row[1]
                frequencies[row[0]] = book
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    authors = {}
    works = {}
    frequencies = load_frequencies(args.path)
    for item in frequencies:
        records = download_data(item)
        if records and len(records) == 1:
            for record in records:
                works[item] = record
                works[item]["count"] = frequencies[item]["count"]
                works[item]["isbn"] = item

    with open('output.tsv', 'w') as output_file:
        csvwriter = csv.writer(output_file, delimiter='\t')
        csvwriter.writerow(["count", "isbn", "author",
                            "title", "LIBRIS", "language"])
        for item in works:
            csvwriter.writerow(works[item].values())
        output_file.close()
