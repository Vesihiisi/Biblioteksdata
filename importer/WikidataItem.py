#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from wikidataStuff.WikidataStuff import WikidataStuff as WDS
from wikidataStuff import helpers as helpers
import pywikibot

import importer_utils as utils

DATA_DIR = "data"


class WikidataItem(object):

    def __init__(self, db_row_dict, repository, data_files, existing, caches):
        self.repo = repository
        self.existing = existing
        self.wdstuff = WDS(self.repo)
        self.raw_data = db_row_dict
        self.caches = caches
        self.problem_report = {}
        self.props = data_files["properties"]
        self.construct_wd_item()

        self.problem_report = {}

    def get_caches(self):
        return self.caches

    def make_q_item(self, qnumber):
        return self.wdstuff.QtoItemPage(qnumber)

    def make_pywikibot_item(self, value):
        val_item = None
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        if utils.string_is_q_item(value):
            val_item = self.make_q_item(value)
        elif value == "novalue":
            val_item = value
        elif isinstance(value, dict) and 'monolingual_value' in value:
            text = value['monolingual_value']
            language = value['lang']
            val_item = pywikibot.WbMonolingualText(text=text,
                                                   language=language)
        elif isinstance(value, dict) and 'quantity_value' in value:
            number = value['quantity_value']
            if 'unit' in value:
                unit = self.wdstuff.QtoItemPage(value["unit"])
            else:
                unit = None
            val_item = pywikibot.WbQuantity(
                amount=number, unit=unit, site=self.repo)
        elif isinstance(value, dict) and 'date_value' in value:
            date_dict = value["date_value"]
            val_item = pywikibot.WbTime(year=date_dict.get("year"),
                                        month=date_dict.get("month"),
                                        day=date_dict.get("day"))
        elif value == "novalue":
            #  raise NotImplementedError
            #  implement Error
            print("Status: novalue will be added here")
        else:
            val_item = value
        return val_item

    def make_statement(self, value):
        if value in ['somevalue', 'novalue']:
            special = True
        else:
            special = False
        return self.wdstuff.Statement(value, special=special)

    def make_qualifier_applies_to(self, value):
        prop_item = self.props["applies_to_part"]
        target_item = self.wdstuff.QtoItemPage(value)
        return self.wdstuff.Qualifier(prop_item, target_item)

    def add_statement(self, prop_name, value, quals=None, ref=None):
        base = self.wd_item["statements"]
        prop = self.props[prop_name]
        if quals is None:
            quals = []
        wd_claim = self.make_pywikibot_item(value)
        statement = self.make_statement(wd_claim)
        for qual in helpers.listify(quals):
            statement.addQualifier(qual)
        base.append({"prop": prop,
                     "value": statement,
                     "ref": ref})

    def make_stated_in_ref(self,
                           value,
                           pub_date=None,
                           ref_url=None,
                           retrieved_date=None):
        item_prop = self.props["stated_in"]
        published_prop = self.props["publication_date"]
        published_claim = None
        if pub_date:
            pub_date = utils.date_to_dict(pub_date, "%Y-%m-%d")
            timestamp = self.make_pywikibot_item({"date_value": pub_date})
            published_claim = self.wdstuff.make_simple_claim(
                published_prop, timestamp)
        source_item = self.wdstuff.QtoItemPage(value)
        source_claim = self.wdstuff.make_simple_claim(item_prop, source_item)
        if ref_url and retrieved_date:
            ref_url_prop = self.props["reference_url"]
            retrieved_date_prop = self.props["retrieved"]

            retrieved_date = utils.date_to_dict(retrieved_date, "%Y-%m-%d")
            retrieved_date = self.make_pywikibot_item(
                {"date_value": retrieved_date})

            ref_url_claim = self.wdstuff.make_simple_claim(
                ref_url_prop, ref_url)
            retrieved_on_claim = self.wdstuff.make_simple_claim(
                retrieved_date_prop, retrieved_date)

            if published_claim:
                ref = self.wdstuff.Reference(
                    source_test=[source_claim, ref_url_claim],
                    source_notest=[published_claim, retrieved_on_claim])
            else:
                ref = self.wdstuff.Reference(
                    source_test=[source_claim, ref_url_claim],
                    source_notest=[retrieved_on_claim])
        else:
            ref = self.wdstuff.Reference(
                source_test=[source_claim],
                source_notest=published_claim
            )
        return ref

    def associate_wd_item(self, wd_item):
        if wd_item is not None:
            self.wd_item["wd-item"] = wd_item

    def set_upload(self, booln):
        self.wd_item["upload"] = booln

    def add_label(self, language, text):
        base = self.wd_item["labels"]
        base.append({"language": language, "value": text})

    def add_description(self, language, text):
        base = self.wd_item["descriptions"]
        base.append({"language": language, "value": text})

    def add_to_report(self, key_name, raw_data, id_no, prop_name=None):
        """
        Add data to problem report json.

        Check if item has an associated Q-number,
        and if that's the case and it's missing
        in the report,
        add it to the report automatically.

        Optionally, assign a Property ID that the data
        should have been used as a value for.

        :param key_name: name of the field containing
                         the problematic data, e.g. the header of the column
        :type key_name: string
        :param raw_data: the data that we failed to process
        :type raw_data: string
        :param id_no: unique id assigned to item, e.g. url
        :type id_no: string
        :param prop_name: name of the property,
                          as stated in the props library file
        :type prop_name: string
        """
        prop = None
        if prop_name:
            if prop_name.startswith('_'):
                prop = prop_name
            else:
                prop = self.props.get(prop_name)
        self.problem_report[key_name] = {"value": raw_data,
                                         "target": prop}
        if "wd-item" not in self.problem_report:
            if self.wd_item["wd-item"] is not None:
                self.problem_report["Q"] = self.wd_item["wd-item"]
            else:
                self.problem_report["Q"] = ""
        self.problem_report["url"] = id_no

    def print_report(self):
        """Print the problem report on screen."""
        print(
            json.dumps(self.problem_report,
                       sort_keys=True,
                       indent=4,
                       ensure_ascii=False,
                       default=utils.datetime_convert)
        )

    def get_report(self):
        """Retrieve the problem report."""
        return self.problem_report

    def construct_wd_item(self):
        self.wd_item = {}
        self.wd_item["upload"] = True
        self.wd_item["statements"] = []
        self.wd_item["labels"] = []
        self.wd_item["descriptions"] = []
        self.wd_item["wd-item"] = None
