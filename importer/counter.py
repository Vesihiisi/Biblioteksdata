#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Count ISBN references on a wiki.

This takes a data file from
https://figshare.com/articles/Wikipedia_Scholarly_Article_Citations/1299540
and counts the ISBN entries,
outputting a tsv file with ISBN : count pairs
sorted from most to least common.
"""
import csv
import argparse
from collections import Counter

OUTPUT = "isbn_sorted.tsv"


def load_references(fname):
    """
    Load reference data.

    Read a tsv file with all refs
    and extract only ones with type: ISBN.
    """
    references = []
    with open(fname, "r") as f_obj:
        reader = csv.reader(f_obj, delimiter='\t')
        for row in reader:
            if row[4] == "isbn":
                references.append(row[5])
    return references


def save_references(sorted_data, fname):
    """Save sorted ref data as tsv file."""
    with open(fname, "w") as f:
        for k, v in references_sorted:
            f.write("{}\t{}\n".format(k, v))
    print("Saved file: {}".format(OUTPUT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    references = load_references(args.path)
    references_sorted = Counter(references).most_common()
    save_references(references_sorted, OUTPUT)
