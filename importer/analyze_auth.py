#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Create mapping tables for Libris auth.

Create frequency-ordered mapping tables
for professions and nationalities in the
Libris auth dataset.
"""
import argparse
import json
import os
from collections import Counter

import importer_utils as utils

MAPPINGS = "mappings"
OUTPUT_NATIONALITIES = "countries"
OUTPUT_PROFESSIONS = "professions"


def is_person(auth_item):
    """Check whether it's a person post."""
    return auth_item["@graph"][1]["@type"] == "Person"


def save_json(sortedlist, fname):
    """Save frequency list to timestamped file."""
    all_json = []
    timestamp = utils.get_current_timestamp()
    filename = "{}_{}.json".format(fname, timestamp)
    for k, v in sortedlist:
        all_json.append({"name": k, "count": v, "q": ""})
    with open(os.path.join(MAPPINGS, filename), 'w') as f:
        json.dump(all_json, f, indent=4,
                  ensure_ascii=False,)


def load_data(path):
    """
    Load a list of files in directory.

    :param limit: return the first x files."
    """
    all_nationalities = []
    all_professions = []
    for fname in os.listdir(path):
        element = utils.load_json(os.path.join(path, fname))
        if not is_person(element):
            continue
        element = element["@graph"]
        nationalities = element[1].get("nationality")
        professions = element[1].get("hasOccupation")
        if professions:
            for p in professions:
                if p.get("label"):
                    for l in p["label"]:
                        all_professions.append(l.lower())
        if nationalities:
            for n in nationalities:
                if n.get("@id"):
                    all_nationalities.append(n["@id"])
    commonest_nat = Counter(all_nationalities).most_common()
    commonest_prof = Counter(all_professions).most_common()
    save_json(commonest_nat, OUTPUT_NATIONALITIES)
    save_json(commonest_prof, OUTPUT_PROFESSIONS)


def main(args):
    load_data(args["dir"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    args = parser.parse_args()
    main(vars(args))
