#!/usr/bin/python
# -*- coding: utf-8  -*-
"""Process all bookrefs from svwp."""
import argparse
import csv


def load_bokrefs(path):
    """Extract okay-looking bookrefs from file."""
    bokrefs = []
    required = ["bokref", "titel"]
    with open(path) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if all(s in row[0].lower() for s in required):
                print(row[0])
                bokrefs.append(row[0])


def main(args):
    """Process file with all refs."""
    bokrefs = load_bokrefs(args.path)
    print(bokrefs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    main(args)
