# -*- coding: utf-8 -*-
"""Upload a WikidataItem to Wikidata."""
from os import path

from wikidataStuff.WikidataStuff import WikidataStuff as WDS
import pywikibot

import importer_utils as utils


MAPPING_DIR = "mappings"
PROPS = utils.load_json(path.join(MAPPING_DIR, "properties.json"))

SUMMARY_TEST = "test"


class Uploader(object):

    TEST_ITEM = "Q4115189"

    def add_labels(self, target_item, labels):
        labels_for_upload = {}
        for label in labels:
            label_content = label['value']
            language = label['language']
            labels_for_upload[language] = label_content
        self.wdstuff.add_multiple_label_or_alias(
            labels_for_upload, target_item)

    def add_descriptions(self, target_item, descriptions):
        descriptions_for_upload = {}
        for description in descriptions:
            desc_content = description['value']
            lang = description['language']
            descriptions_for_upload[lang] = desc_content
        self.wdstuff.add_multiple_descriptions(
            descriptions_for_upload, target_item)

    def add_claims(self, wd_item, claims):
        if wd_item:
            for claim in claims:
                wd_item.get()
                prop = claim["prop"]
                value = claim["value"]
                ref = claim["ref"]
                if prop in ["P569", "P570"]:
                    # Let's check if the target item already has one...
                    dates_in_item = utils.get_value_of_property(
                        wd_item.getID(), prop, self.repo)
                    for date in dates_in_item:
                        if date.precision > value.itis.precision and date.year == value.itis.year:
                            print("!!! Possible duplicate timestamp.")
                            print("precision: {}, year: {}".format(
                                date.precision, date.year))
                self.wdstuff.addNewClaim(prop, value, wd_item, ref)

    def create_new_item(self):
        return self.wdstuff.make_new_item({}, self.summary)

    def get_username(self):
        return pywikibot.config.usernames["wikidata"]["wikidata"]

    def upload(self):
        if self.data["upload"] is False:
            print("SKIPPING ITEM")
            return
        labels = self.data["labels"]
        descriptions = self.data["descriptions"]
        claims = self.data["statements"]
        self.add_labels(self.wd_item, labels)
        self.add_descriptions(self.wd_item, descriptions)
        self.add_claims(self.wd_item, claims)

    def set_wd_item(self):
        if self.live:
            if self.data["wd-item"] is None:
                self.wd_item = self.create_new_item()
                self.wd_item_q = self.wd_item.getID()
            else:
                item_q = self.data["wd-item"]
                self.wd_item = self.wdstuff.QtoItemPage(item_q)
                self.wd_item_q = item_q
        else:
            self.wd_item = self.wdstuff.QtoItemPage(self.TEST_ITEM)
            self.wd_item_q = self.TEST_ITEM

    def __init__(self,
                 data_object,
                 repo,
                 live=False,
                 edit_summary=None):
        self.repo = repo
        self.live = live
        if self.live:
            print("LIVE MODE")
            self.summary = edit_summary
        else:
            print("SANDBOX MODE: {}".format(self.TEST_ITEM))
            self.summary = SUMMARY_TEST
        print("User: {}".format(self.get_username()))
        print("Edit summary: {}".format(self.summary))
        print("---------------")
        self.data = data_object.wd_item
        self.wdstuff = WDS(self.repo, edit_summary=self.summary)
        if self.data["upload"]:
            self.set_wd_item()
