#!/usr/bin/python
# -*- coding: utf-8  -*-
import argparse
import json
import requests

from Person import Person


def is_person(auth_item):
    return auth_item["@graph"][1]["@type"] == "Person"


def make_person(auth_data):
    return Person(data)


def get_from_uri(uri):
    url = "https://libris-qa.kb.se/{}/data.jsonld".format(uri)
    return json.loads(requests.get(url).text)


def get_data(args):
    if args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
    elif args.uri:
        data = get_from_uri(args.uri)
    return data


def main(data):
    if is_person(data):
        person = make_person(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--uri")
    args = parser.parse_args()
    data = get_data(args)
    main(data)
