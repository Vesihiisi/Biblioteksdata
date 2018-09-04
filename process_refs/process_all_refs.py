#!/usr/bin/python
# -*- coding: utf-8  -*-
"""Process all bookrefs from svwp."""
import argparse
import csv
import re
from urllib.parse import urlparse
import mwparserfromhell as parser
from collections import Counter
import importer_utils as utils

OUTPUT_BOOKS = "all_book_refs_sorted.tsv"
OUTPUT_WEBSITES = "all_websites_sorted.tsv"


def save_sorted_websites(sorted_data, fname):
    """Save sorted website data as tsv file."""
    with open(fname, "w") as f:
        f.write("{}\t{}\n".format("count", "website"))
        for k, v in sorted_data:
            f.write("{}\t{}\n".format(v, k))
    print("Saved file: {}".format(fname))


def save_sorted_books(sorted_data, fname):
    """Save sorted book data as tsv file."""
    with open(fname, "w") as f:
        f.write("{}\t{}\t{}\n".format("count", "book", "author"))
        for k, v in sorted_data:
            f.write("{}\t{}\n".format(v, k))
    print("Saved file: {}".format(fname))


def ref_to_template(bokref):
    parsed = parser.parse(bokref)
    templates = parsed.filter_templates()
    for t in templates:
        if t.name.matches("Bokref"):
            return(t)


def bokref_to_work(bokref):
    try:
        title = str(bokref.get("titel").value)
    except ValueError:
        title = ""
    try:
        author = utils.remove_markup(str(bokref.get("författare").value))
    except ValueError:
        try:
            last = bokref.get("efternamn").value
            first = bokref.get("förnamn").value
            author = " ".join([utils.remove_markup(str(first)),
                               utils.remove_markup(str(last))])
        except ValueError:
            author = ""

    if len(title) > 0:
        title = utils.remove_markup(title)
        work = "{}\t{}".format(title, author)
        return work


def load_webrefs(path):
    """Process all url's found in the dumpfile."""
    webrefs = []
    counter = 0
    regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]'
             '|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    with open(path) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            urls = re.findall(regex, row[0])
            for url in urls:
                try:
                    netloc = urlparse(url).netloc
                except ValueError:
                    continue
                if netloc.startswith("www."):
                    netloc = netloc[4:]
                webrefs.append(netloc)
                counter += 1
                if counter % 1000 == 0:
                    print("Processed {} refs.".format(counter))
    return webrefs


def load_bokrefs(path):
    """Extract okay-looking bookrefs from file."""
    bokrefs = []
    required = ["bokref", "titel"]
    counter = 0
    with open(path) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if all(s in row[0].lower() for s in required):
                bokref_tpl = ref_to_template(row[0])
                if bokref_tpl:
                    counter += 1
                    if counter % 1000 == 0:
                        print("Processed {} refs.".format(counter))
                    bokrefs.append(bokref_to_work(bokref_tpl))
    return bokrefs


def get_frequencies_websites(args):
    """Process file with all refs to extract websites."""
    webrefs = load_webrefs(args.path)
    commonest = Counter(webrefs).most_common()
    save_sorted_websites(commonest, OUTPUT_WEBSITES)


def get_frequencies_books(args):
    """Process file with all refs to extract books."""
    bokrefs = load_bokrefs(args.path)
    commonest = Counter(bokrefs).most_common()
    save_sorted_books(commonest, OUTPUT_BOOKS)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--path", required=True)
    args = argparser.parse_args()
    get_frequencies_websites(args)
    get_frequencies_books(args)
