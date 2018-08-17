#!/usr/bin/python
# -*- coding: utf-8  -*-
"""An object representing a Libris person item."""
from WikidataItem import WikidataItem
import importer_utils as utils


class Person(WikidataItem):
    """A person as represented in Libris."""

    URL_BASE = "https://libris.kb.se/katalogisering/{}"

    def set_is(self):
        self.add_statement("is", "Q5", ref=self.source)

    def set_labels(self):
        """
        To do - when can we set labels in
        different languages?
        Nationality tags - swedish, finnish etc.
        can have english etc labels, but not russian...

        NOTE: the same strategy will have to be
        applied to first/last names -- only add those
        to items with ROman source language.
        """
        roman_nationalities = ["e-fi---",
                               "e-sw---"]
        languages = ["sv", "en", "fi"]

        first_name = self.raw_data[1]["givenName"]
        last_name = self.raw_data[1]["familyName"]
        label = "{} {}".format(first_name, last_name)
        self.add_label("sv", label)

        has_nationality = self.raw_data[1].get("nationality")
        if has_nationality:
            nationality = self.raw_data[1]["nationality"][0]["@id"].split(
                "/")[-1]
            if nationality in roman_nationalities:
                for lng in languages:
                    self.add_label(lng, label)

    # def set_first_name(self):
    #     self.first_name = self.raw_data[1]["givenName"]

    # def set_surname(self):
    #     self.surname = self.raw_data[1]["familyName"]

    def set_uri(self):
        uri = self.raw_data[0]["@id"].split("/")[-1]
        self.add_statement("libris_uri", uri)

    def set_selibr(self):
        """Set Selibr identifier."""
        selibr = self.raw_data[0]["controlNumber"]
        self.add_statement("selibr", selibr)

    def set_ids(self):
        """
        Set other authority ID's.

        ISNI numbers are formatted with spaces
        because it's a property constraint.
        Also, the uploader doesn't recognize
        formatted/unformatted ISNI as duplicates.
        """
        allowed_types = ["viaf", "isni"]
        self.auth_ids = []
        bio_section = self.raw_data[1]
        if bio_section.get("identifiedBy"):
            for i in bio_section.get("identifiedBy"):
                if (i["@type"] == "Identifier" and
                   i["typeNote"] in allowed_types):
                    if i["typeNote"] == "isni":
                        i["value"] = utils.format_isni(i["value"])
                    self.add_statement(i["typeNote"], i["value"])

    def set_descriptions(self):
        # NOTE - sometimes they are longish, or messy.. Not sure if we should
        # upload them indiscriminately
        # Maybe detect if there's a full stop, and cut off there?
        # Also: lower-case?
        # Make a dump of some descriptions so that we can
        # make some generalizations.
        bio_info = self.raw_data[1].get("hasBiographicalInformation")
        if bio_info and bio_info[0]["@type"] == "BiographicalNote":
            desc = bio_info[0]["label"]
            self.add_description("sv", desc)

    def set_profession(self):
        """
        To do -- see exactly which professions are present
        and map them.
        """
        bio_section = self.raw_data[1]
        if bio_section.get("hasOccupation"):
            occs = bio_section.get("hasOccupation")[0].get("label")
            for prof in [x.lower() for x in occs]:
                prof_q = self.data_files["professions"].get(prof)
                self.add_statement("profession", prof_q, ref=self.source)
            # can we find examples of multiple professions?

    def set_lifespan(self):
        """
        These should only be uploaded when item doesn't
        already have them? Or is it possible to check
        if item has lower exactness and then upload if
        we have a better one?
        Will be handled in the Uploader....
        """
        born_dict, dead_dict = None, None
        self.lifespan = {"born": None, "dead": None}
        bio_section = self.raw_data[1]
        if not bio_section.get("lifeSpan"):
            return
        life = bio_section["lifeSpan"].split("-")
        born_raw = life[0]
        dead_raw = life[1]
        if len(born_raw) == 4:
            born_dict = utils.date_to_dict(born_raw, "%Y")
        if "birthDate" in bio_section.keys():
            born_long_raw = bio_section["birthDate"]
            if len(born_long_raw) == 8:
                born_dict = utils.date_to_dict(born_long_raw, "%Y%m%d")
        if born_dict:
            born_pwb = self.make_pywikibot_item({"date_value": born_dict})
            self.add_statement("born", born_pwb, ref=self.source)

        if len(dead_raw) == 4:
            dead_dict = utils.date_to_dict(dead_raw, "%Y")
        if "deathDate" in bio_section.keys():
            dead_long_raw = bio_section["deathDate"]
            if len(dead_long_raw) == 8:
                dead_dict = utils.date_to_dict(dead_long_raw, "%Y%m%d")
        if dead_dict:
            dead_pwb = self.make_pywikibot_item({"date_value": dead_dict})
            self.add_statement("dead", dead_pwb, ref=self.source)

    def set_nationality(self):
        """
        To do: see exactly which nationalities are present
        and map.
        """
        has_nationality = self.raw_data[1].get("nationality")
        if has_nationality:
            nationality = self.raw_data[1]["nationality"][0]["@id"].split(
                "/")[-1]
            country = self.data_files["countries"].get(nationality)
            if country:
                self.add_statement("citizenship", country, ref=self.source)

    def create_sources(self):
        uri = self.raw_data[0]["@id"].split("/")[-1]
        url = self.URL_BASE.format(uri)

        publication_date = self.timestamp
        retrieval_date = "2018-08-15"  # replace date of the dump
        self.source = self.make_stated_in_ref("Q1798125",
                                              publication_date,
                                              url, retrieval_date)

    def match_wikidata(self):
        """
        Matching order:
        1. LIBRIS URI
        2. SELIBR
        ...? viaf/isni?

        NOTE
        The Selibr match might not be 1:1? There were
        some problematic ones in the reports.
        Filter out duplicates?
        ---
        Another mode: Use VIAF data to match
        items with VIAF but no other id's --
        search viaf.org to see if it links
        back to the wd item.
        """
        uri = self.raw_data[0]["@id"].split("/")[-1]
        selibr = self.raw_data[0]["controlNumber"]
        uri_match = self.existing.get(uri)
        selibr_match = self.data_files["selibr"].get(selibr)

        if uri_match:
            self.associate_wd_item(uri_match)
        elif selibr_match:
            self.associate_wd_item(selibr_match)

    def set_timestamp(self):
        self.timestamp = self.raw_data[0].get("modified").split("T")[0]

    def __init__(self, raw_data, repository, data_files, existing):
        """Initialize an empty object."""
        WikidataItem.__init__(self, raw_data, repository, data_files, existing)
        self.raw_data = raw_data["@graph"]
        self.set_timestamp()
        self.data_files = data_files
        self.create_sources()

        self.set_ids()
        self.set_selibr()
        self.match_wikidata()

        self.set_is()
        self.set_uri()
        self.set_nationality()
        self.set_lifespan()
        self.set_profession()
        # self.set_surname()
        # self.set_first_name()
        self.set_descriptions()
        self.set_labels()
