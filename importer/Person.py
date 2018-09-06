#!/usr/bin/python
# -*- coding: utf-8  -*-
"""An object representing a Libris person item."""
from WikidataItem import WikidataItem
import importer_utils as utils


class Person(WikidataItem):
    """A person as represented in Libris."""

    URL_BASE = "https://libris.kb.se/katalogisering/{}"
    DUMP_DATE = "2018-08-24"

    def set_is(self):
        """Set is as a person."""
        self.add_statement("is", "Q5", ref=self.source)

    def set_labels(self):
        """Set labels in different languages."""
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

    def set_uri(self):
        """Set Libris URI."""
        uri = self.raw_data[0]["@id"].split("/")[-1]
        self.add_statement("libris_uri", uri, ref=self.source)

    def set_selibr(self):
        """Set Selibr identifier."""
        selibr = self.raw_data[0]["controlNumber"]
        self.add_statement("selibr", selibr)

    def set_ids(self):
        """
        Set VIAF and ISNI id's.

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
                    self.add_statement(i["typeNote"],
                                       i["value"],
                                       ref=self.source)

    def set_descriptions(self):
        """Set the Swedish description."""
        bio_info = self.raw_data[1].get("hasBiographicalInformation")
        if bio_info and bio_info[0]["@type"] == "BiographicalNote":
            desc = bio_info[0]["label"]
            self.add_description("sv", desc)

    def set_profession(self):
        """Set professions of the person."""
        prof_map = self.data_files["professions"]
        bio_section = self.raw_data[1]
        professions = bio_section.get("hasOccupation")
        if professions:
            for p in professions:
                if p.get("label"):
                    for l in p["label"]:
                        prof_to_match = l.lower()
                        prof_q = [x.get("q")
                                  for x in
                                  prof_map if x["name"] == prof_to_match]
                        if prof_q:
                            self.add_statement(
                                "profession", prof_q, ref=self.source)

    def set_lifespan(self):
        """
        Add birth and death dates.

        If the item has both a lifeSpan lump
        and separate birth/deathDate dates, the
        latter one will be selected if more precise.
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
        """Add countries of nationality, converted from MARC-ish code."""
        country_map = self.data_files["countries"]
        nationalities = self.raw_data[1].get("nationality")
        if not nationalities:
            return
        for nat in nationalities:
            if nat.get("@id"):
                nat_q = [x.get("q")
                         for x in
                         country_map if x["name"] == nat["@id"]]
                if nat_q:
                    self.add_statement("citizenship", nat_q, ref=self.source)

    def create_sources(self):
        """
        Create a stated in reference.

        Note that some objects do not have last
        modification date, or any other date,
        in the dump. These seem to be recently created
        items, from summer 2018 onwards, i.e. probably
        native "new Libris" objects, not imported.
        For these we only add retrieval date.
        """
        uri = self.raw_data[0]["@id"].split("/")[-1]
        url = self.URL_BASE.format(uri)

        publication_date = None
        modified = self.raw_data[0].get("modified")
        if modified:
            publication_date = modified.split("T")[0]

        self.source = self.make_stated_in_ref("Q1798125",
                                              publication_date,
                                              url, self.DUMP_DATE)

    def match_wikidata(self):
        """
        Match a Wikidata item.

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
        selibrs = self.data_files["selibr"]
        uri = self.raw_data[0]["@id"].split("/")[-1]
        selibr = self.raw_data[0]["controlNumber"]
        uri_match = self.existing.get(uri)
        selibr_match = selibrs.get(selibr)

        if uri_match:
            self.associate_wd_item(uri_match)
        #  If there's more than one selibr-key associated
        #  with a Q number, exclude this object from the upload.
        #  That way we avoid editing WD items with multiple
        #  P906 (error either on WD or in Libris)
        elif selibr_match:
            selibrs_on_this_q = [x for x in selibrs.keys()
                                 if selibrs[x] == selibr_match]
            if len(selibrs_on_this_q) == 1:
                self.associate_wd_item(selibr_match)
            else:
                self.set_upload(False)
        else:
            self.set_upload(False)

    def set_timestamp(self):
        """Get timestamp of last change of post."""
        self.timestamp = self.raw_data[0].get("modified").split("T")[0]

    def __init__(self, raw_data, repository, data_files, existing):
        """Initialize an empty object."""
        WikidataItem.__init__(self, raw_data, repository, data_files, existing)
        self.raw_data = raw_data["@graph"]
        self.data_files = data_files
        self.create_sources()

        # self.set_selibr()
        self.match_wikidata()

        self.set_is()
        self.set_uri()
        self.set_profession()
        self.set_nationality()
        self.set_ids()
        # self.set_lifespan()
        # self.set_surname()
        # self.set_first_name()
        # self.set_descriptions()
        # self.set_labels()
