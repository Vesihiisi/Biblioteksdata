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

    def agent_to_wikidata(self, agent_tag):
        if agent_tag.get("@id"):
            agent_id = agent_tag.get("@id")
            agent_uri = agent_id.split("/")[-1].split("#")[0]
            match = self.existing.get(agent_uri)
            if match:
                return match

    def set_author(self):
        raw_contribs = self.raw_data[2].get("contribution")
        for contrib in raw_contribs:
            wd_match = None
            roles = contrib.get("role")
            if not roles:
                if contrib.get("@type") == "PrimaryContribution":
                    agent = contrib.get("agent")
                    wd_match = self.agent_to_wikidata(agent)
                else:
                    return
            else:
                for role in roles:
                    if role.get("@id") == "https://id.kb.se/relator/author":
                        agent = contrib.get("agent")
                        wd_match = self.agent_to_wikidata(agent)
            if wd_match:
                self.add_statement("author", wd_match)

    def set_title(self):
        """
        Set title of edition.

        Use language code from set_language();
        if it couldn't be extracted there, it will
        default to 'undefined'.
        """
        raw_title = self.raw_data[1].get("hasTitle")
        if not raw_title:
            return
        if len(raw_title) != 1:
            return
        if raw_title[0].get("@type") == "Title":
            main_title = raw_title[0].get("mainTitle")
            if main_title:
                wd_title = utils.package_monolingual(
                    main_title, self.lang_wikidata)
                self.add_statement("title", wd_title)

    def set_subtitle(self):
        """
        Set subtitle.

        Use language code from set_language();
        if it couldn't be extracted there, it will
        default to 'undefined'.
        """
        raw_subtitle = self.raw_data[1].get("hasTitle")
        if not raw_subtitle:
            return
        if len(raw_subtitle) != 1:
            return
        if raw_subtitle[0].get("subtitle"):
            subtitle = raw_subtitle[0].get("subtitle")
            wd_subtitle = utils.package_monolingual(
                subtitle, self.lang_wikidata)
            self.add_statement("subtitle", wd_subtitle)

    def set_language(self):
        """
        Set language of edition.

        Because this information does not seem to
        have same position in every entry,
        we have to traverse the json for it.
        Save Wikidata-compatible language code
        in self to be re-used for setting
        title/subtitle properties. If no language
        is extracted here, set self.lang_wikidata
        to undefined.
        """
        lang_map = self.data_files["languages"]
        for el in self.raw_data:
            graph = el.get("@graph")
            if graph and len(graph) > 1:
                for el in graph[1]:
                    if graph[1][el] == "Language":
                        edition_lang = graph[1].get("langCode")

        if edition_lang:
            lang_q = [x.get("q")
                      for x in
                      lang_map if x["name"] == edition_lang]
            lang_wikidata = [x.get("wikidata")
                             for x in
                             lang_map if x["name"] == edition_lang]
            if lang_q:
                self.add_statement("language", lang_q[0])
            if lang_wikidata:
                self.lang_wikidata = lang_wikidata[0]
            else:
                self.lang_wikidata = "und"

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

    def set_publication_date(self):
        """Set year of publication."""
        raw_publ = self.raw_data[1].get("publication")
        if not raw_publ:
            return
        for el in raw_publ:
            if el.get('@type') == "PrimaryPublication":
                raw_year = el.get("year")
                if raw_year and utils.legit_year(raw_year):
                    year_dict = {"date_value": {"year": raw_year}}
                    self.add_statement("publication_date", year_dict)

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
        self.set_author()
        self.set_title()
        self.set_subtitle()
        self.set_publication_date()
        self.set_pages()
