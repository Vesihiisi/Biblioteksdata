#!/usr/bin/python
# -*- coding: utf-8  -*-
import pywikibot
import pywikibot.data.sparql as sparql
import wikidataStuff.helpers as helpers


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
