#!/usr/bin/python
# -*- coding: utf-8  -*-
import datetime
import json
import re

import pywikibot
import pywikibot.data.sparql as sparql
import wikidataStuff.helpers as helpers
site_cache = {}


def lowercase_first(text):
    """Convert 1st character of string to lowercase."""
    return text[0].lower() + text[1:]


def get_current_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')


def string_is_q_item(text):
    """Check if a string looks like a WD ID."""
    pattern = re.compile("^Q[0-9]+$", re.I)
    try:
        m = pattern.match(text)
    except TypeError:
        return False
    if m:
        return True
    else:
        return False


def load_json(filename):
    try:
        with open(filename) as f:
            try:
                return json.load(f)
            except ValueError:
                print("Failed to decode file {}.".format(filename))
    except OSError:
        print("File {} does not exist.".format(filename))


def create_site_instance(language, family):
    """Create an instance of a Wiki site (convenience function)."""
    site_key = (language, family)
    site = site_cache.get(site_key)
    if not site:
        site = pywikibot.Site(language, family)
        site_cache[site_key] = site
    return site


def sanitize_wdqs_result(data):
    """
    Strip url component out of wdqs results.

    Source: deprecated wdqsLookup.py.
    Strip out http://www.wikidata.org/entity/
    For dicts it is assumed that it is the key which should be sanitized
    @param data: data to sanitize
    @type data: str, or list of str or dict
    @return: sanitized data
    @rtype: list of str
    """
    if helpers.is_str(data):
        return data.split('/')[-1]
    elif isinstance(data, list):
        for i, d in enumerate(data):
            data[i] = d.split('/')[-1]
        return data
    if isinstance(data, dict):
        new_data = dict()
        for k, v in data.items():
            new_data[k.split('/')[-1]] = v
        return new_data
    else:
        raise pywikibot.Error('sanitize_wdqs_result() requires a string, dict '
                              'or a list of strings. Not a %s' % type(data))


def get_wd_items_using_prop(prop):
    """
    Get WD items that already have some value of a unique ID.

    Even if there are none before we start working,
    it's still useful to have in case an upload is interrupted
    and has to be restarted, or if we later want to enhance
    some items. When matching, these should take predecence
    over any hardcoded matching files.

    The output is a dictionary of ID's and items
    that looks like this:
    {'4420': 'Q28936211', '2041': 'Q28933898'}
    """
    items = {}
    print("WILL NOW DOWNLOAD WD ITEMS THAT USE " + prop)
    query = "SELECT DISTINCT ?item ?value  WHERE {?item p:" + \
        prop + "?statement. OPTIONAL { ?item wdt:" + prop + " ?value. }}"
    sparql_query = sparql.SparqlQuery()
    data = sparql_query.select(query)
    for x in data:
        key = sanitize_wdqs_result(x['item'])
        value = x['value']
        items[value] = key
    print("FOUND {} WD ITEMS WITH PROP {}".format(len(items), prop))
    return items


def get_name(which, namevalue):
    if which == "first":
        name_item = "Q202444"
    elif which == "last":
        name_item = "Q101352"
    query = "SELECT DISTINCT ?item WHERE {?item wdt:P31 wd:" + \
        name_item + ". ?item wdt:P1705 ?value. FILTER(str(?value) = '" + \
        namevalue + "')}"
    print("Querying WD for {} name {}.".format(which, namevalue))
    sparql_query = sparql.SparqlQuery()
    data = sparql_query.select(query)
    if len(data) == 1:
        return sanitize_wdqs_result(data[0]['item'])


def date_to_dict(datestring, dateformat):
    """
    Convert a date to a pwb-friendly dictionary.

    Can handle:
        * day dates, "2009-09-31",
        * month dates, "2009-09",
        * year dates, "2009"

    :param datestring: a string representing a date timestamp,
                       for example: "2009-09-31".
    :param datestring: a string key for interpreting the timestamp,
                       for example "%Y-%m-%d" which is the key for
                       the above timestamp.
    """
    date_dict = {}
    date_obj = datetime.datetime.strptime(datestring, dateformat)
    date_dict["year"] = date_obj.year
    if "%m" in dateformat:
        date_dict["month"] = date_obj.month
    if "%d" in dateformat:
        date_dict["day"] = date_obj.day
    return date_dict


def format_isni(st):
    """Format ISNI id by inserting space after every 4 chars."""
    return ' '.join(st[i:i + 4] for i in range(0, len(st), 4))


def get_value_of_property(q_number, property_id, site):
    results = []
    item = pywikibot.ItemPage(site, q_number)
    if item.exists() and item.claims.get(property_id):
        for claim in item.claims.get(property_id):
            target = claim.getTarget()
            if isinstance(target, pywikibot.ItemPage):
                target = target.getID()
            results.append(target)
    return results
