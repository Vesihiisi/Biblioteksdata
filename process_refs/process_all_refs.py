#!/usr/bin/python
# -*- coding: utf-8  -*-
"""Process all bookrefs from svwp."""
import argparse
import csv
import mwparserfromhell as parser

import importer_utils as utils


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
        author = str(bokref.get("författare").value)
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
        work = {"title": title, "author": author}
        return work


def load_bokrefs(path):
    """Extract okay-looking bookrefs from file."""
    bokrefs = []
    required = ["bokref", "titel"]
    with open(path) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if all(s in row[0].lower() for s in required):
                bokrefs.append(row[0])
                bokref_tpl = ref_to_template(row[0])
                if bokref_tpl:
                    work = bokref_to_work(bokref_tpl)
                    print(work)


def main(args):
    """Process file with all refs."""
    bokrefs = load_bokrefs(args.path)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--path", required=True)
    args = argparser.parse_args()
    main(args)
