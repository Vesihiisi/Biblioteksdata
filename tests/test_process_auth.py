#!/usr/bin/python
# -*- coding: utf-8  -*-
import unittest
import importer.process_auth as process


class TestAuthProcessing(unittest.TestCase):

    def setUp(self):
        self.strindberg = process.get_from_uri(
            "tr574vdc33gk2cc")  # dead, complex
        self.runeberg = process.get_from_uri("rp369m0923fhv01")  # dead, simple
        self.enckell = process.get_from_uri(
            "xv8bb94g23ng552")  # living, simple
        self.organisation = process.get_from_uri(
            "64jljffq17m41sr")  # non-person

    def test_get_selibr(self):
        selibr = process.get_selibr(self.enckell)
        self.assertEqual(selibr, "185114")

    def test_get_ids(self):
        ids = [{"type": "viaf", "value": "74098998"}, {
            "type": "isni", "value": "0000000051964492"}]
        get_ids = process.get_ids(self.enckell)
        self.assertEqual(get_ids, ids)

    def test_get_ids_none(self):
        get_ids = process.get_ids(self.runeberg)
        self.assertEqual(len(get_ids), 0)

    def test_is_person_pass(self):
        personhood = process.is_person(self.enckell)
        self.assertTrue(personhood)

    def test_is_person_fail(self):
        personhood = process.is_person(self.organisation)
        self.assertFalse(personhood)

    def test_get_surname_1(self):
        surname = process.get_surname(self.enckell)
        self.assertEqual(surname, "Enckell")

    def test_get_first_name(self):
        first_name = process.get_first_name(self.enckell)
        self.assertEqual(first_name, "Martin")

    def test_get_descriptions_1(self):
        desc = ["Finlandsvensk författare"]
        self.assertEqual(process.get_descriptions(self.enckell), desc)

    def test_get_dates_simple_living(self):
        dates = {"born": "1954", "dead": None}
        self.assertEqual(process.get_dates(self.enckell), dates)

    def test_get_dates_simple_dead(self):
        dates = {"born": "1838", "dead": "1920"}
        self.assertEqual(process.get_dates(self.runeberg), dates)


if __name__ == '__main__':
    unittest.main()
