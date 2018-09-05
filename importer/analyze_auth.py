#!/usr/bin/python
# -*- coding: utf-8  -*-
import argparse
import json
import os
from collections import Counter

import importer_utils as utils

MAPPINGS = "mappings"
OUTPUT_NATIONALITIES = "countries.json"


def is_person(auth_item):
    """Check whether it's a person post."""
    return auth_item["@graph"][1]["@type"] == "Person"


def save_json(sortedlist, fname):
    all_json = []
    for k, v in sortedlist:
        all_json.append({"name": k, "count": v, "q": ""})
    with open(os.path.join(MAPPINGS, fname), 'w') as f:
        json.dump(all_json, f)


def load_data(path):
    """
    Load a list of files in directory.

    :param limit: return the first x files."
    """
    all_nationalities = []
    for fname in os.listdir(path):
        element = utils.load_json(os.path.join(path, fname))
        if not is_person(element):
            continue
        element = element["@graph"]
        nationalities = element[1].get("nationality")
        if nationalities:
            for n in nationalities:
                if n.get("@id"):
                    all_nationalities.append(n["@id"])
    commonest_nat = Counter(all_nationalities).most_common()
    save_json(commonest_nat, OUTPUT_NATIONALITIES)


def main(args):
    load_data(args["dir"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    args = parser.parse_args()
    main(vars(args))
