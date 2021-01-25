#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
xxx.
"""
import argparse
import random
import utils

PROPERTIES = {"viaf": "P214",
              "selibr": "P906"}


def make_editgroups_summary(basetext):
    """xx."""
    randomhash = "{:x}".format(random.randrange(0, 2**48))
    editgroup = "([[:toollabs:editgroups/b/CB/{}|details]])".format(randomhash)
    return "{} {}".format(basetext, editgroup)


def is_old_selibr(idno):
    """xx."""
    return idno.isdecimal() and len(idno) < 10


def get_humans_with_selibr_no_viaf():
    """xx."""
    return utils.run_query("get_humans_with_selibr_no_viaf.rq")


def get_humans_with_viaf_no_selibr():
    return utils.run_query("get_humans_with_viaf_no_selibr.rq")


def main(args):
    """xxxxx."""
    viaf_file = args.path
    if args.action == "add_viaf_from_selibr":
        add_viaf_from_selibr(viaf_file, args.upload)
    elif args.action == "add_selibr_from_viaf":
        add_selibr_from_viaf(viaf_file, args.upload)


def add_selibr_from_viaf(viaf_file, upload):
    """
    1. identify VIAF posts that have a SELIBR
    2. check if therethere is a Wikidata item with this VIAF
    3. but it does not have selibr
    4. Add SELIBR to those items.
    """
    edit_summary = make_editgroups_summary("Adding SELIBR based on VIAF")
    with open(viaf_file) as myfile:
        for line in myfile:
            cleanline = is_selibr_line(line)
            if cleanline:
                viaf = cleanline[0]
                selibr = cleanline[1]
                onwikidata = utils.run_query("get_item_with_property_value.rq",
                (PROPERTIES["viaf"], viaf))
                if not onwikidata:
                    continue
                q = onwikidata[0]["item"]
                if utils.is_human(q):
                    selibr_value = utils.get_claim(q, PROPERTIES["selibr"])
                    if not selibr_value:
                        print(q)
                        if upload:
                            utils.wd_add_unique_claim(q,
                                                      {"prop":    PROPERTIES["selibr"],
                                                       "value": selibr}, edit_summary)



def is_selibr_line(viaf_file_line):
    """fsf."""
    cleanline = viaf_file_line.rstrip('\n').split("\t")
    if cleanline[1].startswith("SELIBR|"):
        selibr = cleanline[1].split("|")[-1]
        if is_old_selibr(selibr):
            return [cleanline[0].split("/")[-1], selibr]


def add_viaf_from_selibr(viaf_file, upload):
    """xxx."""
    edit_summary = make_editgroups_summary("Adding VIAF based on SELIBR")
    humans_with_selibr_no_viaf = get_humans_with_selibr_no_viaf()
    with open(viaf_file) as myfile:
        for line in myfile:
            cleanline = is_selibr_line(line)
            if cleanline:
                human_on_wikidata = [
                    x for x in humans_with_selibr_no_viaf if x["selibr"] == cleanline[1]]
                if human_on_wikidata:
                    item_to_add_viaf_to = human_on_wikidata[0]["item"]
                    viaf = cleanline[0]
                    print("{} → {}".format(item_to_add_viaf_to, viaf))
                    if upload:
                        utils.wd_add_unique_claim(item_to_add_viaf_to,
                                                  {"prop": PROPERTIES["viaf"],
                                                   "value": viaf},
                                                  edit_summary)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("--path", required=True)
    PARSER.add_argument("--action", required=True,
                        choices=['add_viaf_from_selibr', 'add_selibr_from_viaf'])
    PARSER.add_argument("--upload", action='store_true')
    ARGS = PARSER.parse_args()
    main(ARGS)
