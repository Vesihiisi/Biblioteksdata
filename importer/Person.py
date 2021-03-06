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

    def get_first_name(self):
        """Get first name from raw data."""
        return self.raw_data[1].get("givenName")

    def get_last_name(self):
        """Get last name from raw data."""
        return self.raw_data[1].get("familyName")

    def add_to_cache(self, cache_name, raw_data, match):
        """Add a raw_data : match pair to cache."""
        self.caches[cache_name][raw_data] = match

    def set_first_name(self):
        """
        Set first name.

        Use the cache if possible, otherwise query Wikidata.
        """
        raw_first_name = self.get_first_name()
        if (not raw_first_name or
                not self.nationality_in_latin_country()):
            return

        multiple_names = raw_first_name.split(" ")
        for raw_part in multiple_names:
            if "." in raw_part:
                # ignore initials like "D."
                continue
            if raw_part in self.caches["first_name"]:
                print("{} found in cache.".format(raw_part))
                first_name = self.caches["first_name"].get(raw_part)
            else:
                first_name = utils.get_name("first", raw_part)
                self.add_to_cache("first_name", raw_part, first_name)

            if first_name:
                print("First name {} matched: {}.".format(
                    raw_part, first_name))
                self.add_statement("first_name", first_name, ref=self.source)
            else:
                print("First name {} not matched.".format(raw_part))
                self.add_to_report(
                    "givenName", raw_part, self.url, "first_name")

    def set_surname(self):
        """
        Set surname.

        Use the cache if possible, otherwise query Wikidata.
        """
        raw_surname = self.get_last_name()
        if (not raw_surname or
                not self.nationality_in_latin_country()):
            return

        if raw_surname in self.caches["surname"]:
            print("{} found in cache.".format(raw_surname))
            surname = self.caches["surname"].get(raw_surname)
        else:
            surname = utils.get_name("last", raw_surname)
            self.add_to_cache("surname", raw_surname, surname)

        if surname:
            print("Surname {} matched: {}.".format(raw_surname, surname))
            self.add_statement("last_name", surname, ref=self.source)
        else:
            print("Surname {} not matched.".format(raw_surname))
            self.add_to_report(
                "familyName", raw_surname, self.url, "last_name")

    def nationality_in_latin_country(self):
        """Check if nationality is in a country with Latin script."""
        latin_countries = [x["country"] for
                           x in self.data_files["latin_countries"]]
        return any(x in self.nationality for x in latin_countries)

    def set_labels(self):
        """
        Set labels in different languages.

        Languages are determined by nationality.
        No nationality or country with non-Latin
        script: Label only in sv.
        Country with Latin script: label in several
        Latin languages.
        """
        first = self.get_first_name()
        last = self.get_last_name()

        if first and last:
            label = "{} {}".format(first, last)
            if self.nationality_in_latin_country():
                languages = self.data_files["latin_languages"]
            else:
                languages = ["sv"]
            for lang in languages:
                self.add_label(lang, label)

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
                        i["typeNote"] in allowed_types and
                        i.get("value")):
                    if i["typeNote"] == "isni":
                        i["value"] = utils.format_isni(i["value"])
                    self.add_statement(i["typeNote"],
                                       i["value"],
                                       ref=self.source)

    def set_descriptions(self):
        """Set the Swedish description."""
        MAX_WORDS = 5
        bad_words = ["birthday.se", "lc auth", "ämne"]
        bad_initial = ["NE:", "DB:"]
        bio_info = self.raw_data[1].get("hasBiographicalInformation")
        if bio_info and bio_info[0]["@type"] == "BiographicalNote":
            desc = bio_info[0]["label"]
            if type(desc) is list:
                desc = desc[0]

            if any(word in desc.lower() for word in bad_words):
                return
            if not desc.lower()[0].isalpha():
                return
            if desc.startswith(tuple(bad_initial)):
                desc = desc.split(":")[0].strip()
            if len(desc.split(" ")) <= MAX_WORDS:
                desc = utils.lowercase_first(desc)
                if desc.startswith("ämne"):
                    return
                if desc.endswith("."):
                    desc = desc[:-1]
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
                        if prof_q and len(prof_q[0]) > 0:
                            self.add_statement(
                                "profession", prof_q, ref=self.source)
                        else:
                            self.add_to_report(
                                "hasOccupation", l, self.url, "profession")

    def is_valid_lifespan(self, lifespan):
        bad_keywords = ["eller", "el.",
                        "fl.", "..",
                        "ca", "?", "verksam"]
        if lifespan.isdigit():
            return False
        if any(keyword in lifespan for keyword in bad_keywords):
            return False
        if not any(char.isdigit() for char in lifespan):
            return False
        return True

    def clean_up_lifespan(self, lifespan):
        lifespan = lifespan.replace("–", "-")
        lifespan = lifespan.replace("d.", "-")
        if "b." in lifespan:
            lifespan = lifespan.replace("b.", "f.")
        if "f." in lifespan:
            lifespan = lifespan.replace("f.", "") + "-"
        return lifespan.split("-")

    def set_lifespan(self):
        """
        Add birth and death dates.

        If the item has both a lifeSpan lump
        and separate birth/deathDate dates, the
        latter one will be selected if more precise.
        """
        bad_lifespan = True
        born_dict, dead_dict = None, None
        self.lifespan = {"born": None, "dead": None}
        bio_section = self.raw_data[1]
        if not bio_section.get("lifeSpan"):
            return
        if self.is_valid_lifespan(bio_section["lifeSpan"]):
            life = self.clean_up_lifespan(bio_section["lifeSpan"])
            if len(life) == 2:
                born_raw = life[0].strip()
                dead_raw = life[1].strip()
                if len(born_raw) == 4 and born_raw.isdigit():
                    bad_lifespan = False
                    born_dict = utils.date_to_dict(born_raw, "%Y")
                if len(dead_raw) == 4 and dead_raw.isdigit():
                    bad_lifespan = False
                    dead_dict = utils.date_to_dict(dead_raw, "%Y")

        if bad_lifespan:
            self.add_to_report("lifeSpan",
                               bio_section.get("lifeSpan"),
                               self.url)

        if "birthDate" in bio_section.keys():
            born_long_raw = bio_section["birthDate"]
            if len(born_long_raw) == 8:
                born_dict = utils.date_to_dict(born_long_raw, "%Y%m%d")

        if "deathDate" in bio_section.keys():
            dead_long_raw = bio_section["deathDate"]
            if len(dead_long_raw) == 8:
                dead_dict = utils.date_to_dict(dead_long_raw, "%Y%m%d")

        if born_dict:
            born_pwb = self.make_pywikibot_item({"date_value": born_dict})
            self.add_statement("born", born_pwb, ref=self.source)
        if dead_dict:
            dead_pwb = self.make_pywikibot_item({"date_value": dead_dict})
            self.add_statement("dead", dead_pwb, ref=self.source)

    def get_nationalities(self):
        nationalities = []
        item_nationalities = self.raw_data[1].get("nationality")
        if item_nationalities:
            for nat in item_nationalities:
                if nat.get("@id"):
                    nationalities.append(nat["@id"])
        return nationalities

    def set_nationality(self):
        """Add countries of nationality, converted from MARC-ish code."""
        self.nationality = []
        country_map = self.data_files["countries"]
        nationalities = self.get_nationalities()
        for nat in nationalities:
            nat_q = [x.get("q")
                     for x in
                     country_map if x["name"] == nat]
            if nat_q and len(nat_q[0]) > 0:
                self.nationality.append(nat_q[0])
                self.add_statement("citizenship", nat_q, ref=self.source)
            else:
                self.add_to_report(
                    "nationality", nat, self.url, "citizenship")

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
        self.url = url

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
        self.create_sources()

        # self.set_selibr()
        self.match_wikidata()

        self.set_is()
        self.set_uri()
        self.set_profession()
        self.set_nationality()
        self.set_labels()
        self.set_ids()
        self.set_lifespan()
        self.set_surname()
        self.set_first_name()
        self.set_descriptions()
