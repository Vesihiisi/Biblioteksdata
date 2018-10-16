#!/usr/bin/python
# -*- coding: utf-8  -*-
"""An object representing a Libris edition item."""
import re

from WikidataItem import WikidataItem
import importer_utils as utils


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

    def set_language(self):
        lang_map = self.data_files["languages"]
        edition_lang = self.raw_data[4]["@graph"][1].get("langCode")
        if edition_lang:
            lang_q = [x.get("q")
                      for x in
                      lang_map if x["name"] == edition_lang]
            if lang_q:
                self.add_statement("language", lang_q[0])

    def set_pages(self):
        """
        Set number of pages.

        Only works if there's exactly one
        'extent' statement that contains
        exactly one numeric content.
        """
        extent = self.raw_data[1].get("extent")
        if len(extent) != 1:
            return
        if extent[0].get("label"):
            extent_labels = extent[0]["label"]
            if len(extent_labels) != 1:
                return
            number_strings = re.findall(r"\d+", extent_labels[0])
            if len(number_strings) == 1:
                no_pages = utils.package_quantity(number_strings[0])
                self.add_statement("pages", no_pages)

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
        self.set_language()
        self.set_pages()
