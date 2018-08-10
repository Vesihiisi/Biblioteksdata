#!/usr/bin/python
# -*- coding: utf-8  -*-
"""An object representing a Libris work item."""


class Work(object):
    """A work as represented in Libris."""

    def add_wikidata(self, existing_works):
        """Add possible Wikidata connections."""
        if self.libris and self.libris in existing_works["libris"].keys():
            self.wikidata = existing_works["libris"][self.libris]
        elif self.searched_isbn in existing_works["isbn13"].keys():
            self.wikidata = existing_works["isbn13"][self.searched_isbn]
            print(self.title)
        elif self.searched_isbn in existing_works["isbn10"].keys():
            self.wikidata = existing_works["isbn10"][self.searched_isbn]
            print(self.title)

    def set_language(self):
        """Set the language if possible."""
        if "language" in self.libris_raw.keys():
            self.language = self.libris_raw["language"]

    def set_creator(self):
        """Set the creator if possible."""
        if "creator" in self.libris_raw.keys():
            self.creator = self.libris_raw["creator"]

    def set_title(self):
        """Set the title."""
        self.title = self.libris_raw["title"]

    def set_isbn(self):
        """Set ISBN as a list, as some works have multiple."""
        if "isbn" in self.libris_raw.keys():
            if isinstance(self.libris_raw["isbn"], str):
                self.isbn = [self.libris_raw["isbn"]]
            else:
                self.isbn = self.libris_raw["isbn"]

    def set_libris(self):
        """Set Libris identifier."""
        self.libris = self.libris_raw["identifier"].split("/")[-1]

    def load_libris_data(self, libris_raw):
        """Convert raw Libris data to properties."""
        self.libris_raw = libris_raw
        self.set_title()
        self.set_isbn()
        self.set_libris()
        self.set_creator()
        self.set_language()

    def __init__(self):
        """Initialize an empty object."""
        self.libris = ""
        self.title = ""
        self.isbn = ""
        self.libris = ""
        self.creator = ""
        self.language = ""
        self.wikidata = ""
