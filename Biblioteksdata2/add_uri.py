#!/usr/bin/python
# -*- coding: utf-8  -*-
import argparse
import json
import logging
import pywikibot
import pywikibot.data.sparql as sparql
import requests
from requests.exceptions import ConnectionError
from pywikibot.exceptions import OtherPageSaveError
import time
from datetime import date

SLEEP_LENGTH = 10

LIBRIS_API = {"authorities": "https://libris.kb.se/auth/{}",
              "editions": "https://libris.kb.se/resource/bib/{}"}
LIBRIS_URL = "https://libris.kb.se/{}"

EDIT_SUMMARY = "Adding Libris URI based on Libris ID"

QUERIES = ["editions", "authorities"]

WIKIDATA = {"libris_uri": "P5587",
            "libris": "Q1798125",
            "stated_in": "P248",
            "published": "P577",
            "reference_url": "P854"}


def get_query(query_name):
    with open('{}.rq'.format(query_name)) as query_file:
        logging.info("Loaded query file: {}".format(query_name))
        return query_file.read()


def get_candidates(query_name):
    query = get_query(query_name)
    candidates = []
    sparql_query = sparql.SparqlQuery()
    data = sparql_query.select(query)
    for x in data:
        candidates.append((x["item"].split("/")[-1], x["librised"]))
    logging.info("{}: Retrieved {} candidates.".format(query_name,
                                                       len(candidates)))
    return candidates


def extract_uri(librised_content):
    return librised_content["@id"].split("/")[-1]


def extract_modified_date(librised_content):
    raw_date = librised_content["modified"].split("T")[0]
    split_date = raw_date.split("-")
    return {"year": int(split_date[0]),
            "month": int(split_date[1]),
            "day": int(split_date[2])}


def retrieve_libris_data(librised, query_type):
    address = LIBRIS_API[query_type].format(librised)
    headers = {'Accept': 'application/json'}
    logging.info("Retrieving data from {}.".format(address))
    libris_content = json.loads(requests.get(address, headers=headers).text)
    uri = extract_uri(libris_content)
    modified_date = extract_modified_date(libris_content)
    url = LIBRIS_URL.format(uri)
    return {"uri": uri, "published": modified_date, "url": url}


def has_claim(property, itempage):
    claims = itempage.get('claims')
    return property in claims['claims']


def upload_uri(qid, processed_libris_post, query_type):
    # qid = "Q4115189"
    uri = processed_libris_post["uri"]
    published = processed_libris_post["published"]
    website = processed_libris_post["url"]
    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, qid)
    today = date.today()
    # check immediately before adding
    if not has_claim(WIKIDATA["libris_uri"], item):
        uri_claim = pywikibot.Claim(repo, WIKIDATA["libris_uri"])
        uri_claim.setTarget(uri)

        published_claim = pywikibot.Claim(repo, WIKIDATA["published"])
        published_date = pywikibot.WbTime(year=published["year"],
                                          month=published["month"],
                                          day=published["day"])
        published_claim.setTarget(published_date)

        stated_in_claim = pywikibot.Claim(repo, WIKIDATA["stated_in"])
        stated_in_claim.setTarget(pywikibot.ItemPage(repo, WIKIDATA["libris"]))

        website_claim = pywikibot.Claim(repo, WIKIDATA["reference_url"])
        website_claim.setTarget(website)

        retrieved_date = pywikibot.WbTime(year=today.year,
                                          month=today.month,
                                          day=today.day)
        retrieved_claim = pywikibot.Claim(repo, 'P813')
        retrieved_claim.setTarget(retrieved_date)

        uri_claim.addSources([stated_in_claim,
                              website_claim,
                              published_claim,
                              retrieved_claim])
        logging.info("Uploading {} {} to {}.".format("URI", uri, qid))
        item.addClaim(uri_claim, summary=EDIT_SUMMARY)


def main(arguments):
    logname = "{}.log".format(
        time.strftime("%Y-%m-%d %H:%M:%S"))
    print("Logging to {}.".format(logname))
    logging.basicConfig(filename=logname,
                        filemode='a',
                        format='%(asctime)s;%(levelname)s;%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)
    for query_type in QUERIES:
        candidates = get_candidates(query_type)
        for candidate in candidates:
            qid = candidate[0]
            librised = candidate[1]
            try:
                processed_libris_post = retrieve_libris_data(librised,
                                                             query_type)
            except (ValueError, ConnectionError) as e:
                logging.error(
                    "Couldn't process Libris ID {} (in {}).".format(librised,
                                                                    qid))
                logging.error(e)
                continue
            if arguments.get("live"):
                try:
                    upload_uri(qid, processed_libris_post, query_type)
                except OtherPageSaveError as e:
                    logging.error("Couldn't save edit in {}.".format(qid))
                    logging.error(e)
            time.sleep(SLEEP_LENGTH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action='store_true')
    args = parser.parse_args()
    main(vars(args))
