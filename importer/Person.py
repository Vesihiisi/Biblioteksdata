#!/usr/bin/python
# -*- coding: utf-8  -*-
"""An object representing a Libris person item."""


class Person(object):
    """A person as represented in Libris."""

    def set_first_name(self):
        self.first_name = self.raw_data[1]["givenName"]

    def set_surname(self):
        self.surname = self.raw_data[1]["familyName"]

    def set_uri(self):
        self.uri = self.raw_data[0]["@id"].split("/")[-1]

    def set_ids(self):
        allowed_types = ["viaf", "isni"]
        self.auth_ids = []
        bio_section = self.raw_data[1]
        if bio_section.get("identifiedBy"):
            for i in bio_section.get("identifiedBy"):
                if (i["@type"] == "Identifier" and
                   i["typeNote"] in allowed_types):
                    self.auth_ids.append(
                        {"type": i["typeNote"],
                         "value": i["value"]})

    def set_descriptions(self):
        self.descriptions = []
        bio_info = self.raw_data[1].get("hasBiographicalInformation")
        if bio_info:
            for el in bio_info:
                if el["@type"] == "BiographicalNote":
                    self.descriptions.append(el["label"])

    def set_occupation(self):
        bio_section = self.raw_data[1]
        if bio_section.get("hasOccupation"):
            occs = bio_section.get("hasOccupation")[0].get("label")
            self.occupation = [x.lower() for x in occs]

    def set_lifespan(self):
        self.lifespan = {"born": None, "dead": None}
        bio_section = self.raw_data[1]
        life = bio_section["lifeSpan"].split("-")
        if len(life[0]) == 4:
            self.lifespan["born"] = life[0]
        if len(life[1]) == 4:
            self.lifespan["dead"] = life[1]
        if "birthDate" in bio_section.keys():
            self.lifespan["born"] = bio_section["birthDate"]
        if "deathDate" in bio_section.keys():
            self.lifespan["dead"] = bio_section["deathDate"]

    def set_selibr(self):
        """Set Selibr identifier."""
        self.selibr = self.raw_data[0]["controlNumber"]

    def set_nationality(self):
        """http://www.loc.gov/marc/geoareas/introduction.pdf"""
        self.nationality = self.raw_data[1]["nationality"][0]["@id"].split(
            "/")[-1]

    def __init__(self, raw_data):
        """Initialize an empty object."""
        self.raw_data = raw_data["@graph"]
        self.set_ids()
        self.set_selibr()
        self.set_uri()
        self.set_nationality()
        self.set_lifespan()
        self.set_occupation()
        self.set_surname()
        self.set_first_name()
        self.set_descriptions()
