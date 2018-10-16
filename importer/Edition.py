#!/usr/bin/python
# -*- coding: utf-8  -*-
"""An object representing a Libris edition item."""
from WikidataItem import WikidataItem
import importer_utils as utils


class Edition(WikidataItem):
    """An Edition as represented in Libris."""

    URL_BASE = "https://libris.kb.se/katalogisering/{}"
    DUMP_DATE = "2018-08-24"  # update when dump

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
