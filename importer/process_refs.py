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
    """Some ISBN nos in Libris have ;"""
    return re.sub('[^\w\s]', '', input)


def load_frequencies(fname):
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


def is_match(idno, record):
    isbn_in_libris = record["isbn"]
    if isinstance(isbn_in_libris, str):
        if only_digits(isbn_in_libris) == idno:
            return True
    elif isinstance(isbn_in_libris, list):
        for potential_isbn in isbn_in_libris:
            if only_digits(potential_isbn) == idno:
                return True
    return False


def download_data(isbn):
    book_url = URL.format(isbn)
    book_data = json.loads(requests.get(book_url).text)
    return book_data["xsearch"]["records"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    authors = {}
    works = {}
    frequencies = load_frequencies(args.path)
    for item in frequencies:
        book_url = URL.format(item)
        book_data = json.loads(requests.get(book_url).text)
        records = book_data["xsearch"]["records"]
        if records > 0:
            for record in book_data["xsearch"]["list"]:
                if is_match(item, record):
                    works[item] = {}
                    works[item]["count"] = frequencies[item]["count"]
                    works[item]["isbn"] = item
                    if "creator" in record.keys():
                        creator = record["creator"]
                        count = frequencies[item]["count"]
                        works[item]["author"] = creator
                        if creator not in authors.keys():
                            authors[creator] = int(count)
                        else:
                            authors[creator] = authors[creator] + int(count)
                    else:
                        works[item]["author"] = ""
                    works[item]["title"] = record["title"]
                    works[item]["libris"] = record["identifier"].split(
                        "/")[-1]
                    works[item]["language"] = record["language"]
                    print(works[item])

    with open('output.tsv', 'w') as output_file:
        csvwriter = csv.writer(output_file, delimiter='\t')
        csvwriter.writerow(["count", "isbn", "author",
                            "title", "LIBRIS", "language"])
        for item in works:
            csvwriter.writerow(works[item].values())
        output_file.close()
    with open('output_authors.tsv', 'w') as output_file:
        csvwriter = csv.writer(output_file, delimiter='\t')
        csvwriter.writerow(["author", "count"])
        for item in authors:
            csvwriter.writerow([item, authors[item]])
        output_file.close()
