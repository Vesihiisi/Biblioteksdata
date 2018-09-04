#!/usr/bin/python
# -*- coding: utf-8  -*-
"""Process all bookrefs from svwp."""
import argparse
import csv
import mwparserfromhell as parser
from collections import Counter
import importer_utils as utils

OUTPUT = "all_refs_sorted.tsv"


def save_sorted(sorted_data, fname):
    """Save sorted  data as tsv file."""
    with open(fname, "w") as f:
        f.write("{}\t{}\t{}\n".format("count", "book", "author"))
        for k, v in sorted_data:
            f.write("{}\t{}\n".format(v, k))
    print("Saved file: {}".format(OUTPUT))


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


def main(args):
    """Process file with all refs."""
    bokrefs = load_bokrefs(args.path)
    commonest = Counter(bokrefs).most_common()
    save_sorted(commonest, OUTPUT)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--path", required=True)
    args = argparser.parse_args()
    main(args)
