#!/usr/bin/python
# -*- coding: utf-8  -*-
"""An object representing a Libris edition item."""
from WikidataItem import WikidataItem
# import importer_utils as utils


class Edition(WikidataItem):
    """An Edition as represented in Libris."""

    URL_BASE = "https://libris.kb.se/katalogisering/{}"
    DUMP_DATE = "2018-08-24"  # update when dump

    def set_is(self):
        edition = "Q3331189"
        self.add_statement("is", edition)

    def match_wikidata(self):
        uri = self.raw_data[0]["@id"].split("/")[-1]
        uri_match = self.existing.get(uri)
        if uri_match:
            self.associate_wd_item(uri_match)

    def set_uri(self):
        uri = self.raw_data[0]["@id"].split("/")[-1]
        self.add_statement("libris_uri", uri)

    def __init__(self, raw_data, repository, data_files, existing, cache):
        """Initialize an empty object."""
        WikidataItem.__init__(self,
                              raw_data,
                              repository,
                              data_files,
                              existing,
                              cache)
        self.raw_data = raw_data["@graph"]
        self.data_files = data_files

        self.match_wikidata()
        self.set_uri()
        self.set_is()
