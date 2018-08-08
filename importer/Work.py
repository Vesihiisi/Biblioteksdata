#!/usr/bin/python
# -*- coding: utf-8  -*-


class Work(object):

    def add_wikidata(self, existing_works):
        if self.libris and self.libris in existing_works["libris"].keys():
            self.wikidata = existing_works["libris"][self.libris]
            print(self.wikidata)

    def set_language(self):
        if "language" in self.libris_raw.keys():
            self.language = self.libris_raw["language"]

    def set_creator(self):
        if "creator" in self.libris_raw.keys():
            self.creator = self.libris_raw["creator"]

    def set_title(self):
        self.title = self.libris_raw["title"]

    def set_isbn(self):
        if "isbn" in self.libris_raw.keys():
            if isinstance(self.libris_raw["isbn"], str):
                self.isbn = [self.libris_raw["isbn"]]
            else:
                self.isbn = self.libris_raw["isbn"]

    def set_libris(self):
        self.libris = self.libris_raw["identifier"].split("/")[-1]

    def load_libris_data(self, libris_raw):
        self.libris_raw = libris_raw
        self.set_title()
        self.set_isbn()
        self.set_libris()
        self.set_creator()
        self.set_language()

    def __init__(self):
        self.libris = ""
        self.title = ""
        self.isbn = ""
        self.libris = ""
        self.creator = ""
        self.language = ""
        self.wikidata = ""
