#!/usr/bin/python
# -*- coding: utf-8  -*-
import unittest
import importer.process_auth as process
from importer.Person import Person


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
        person = Person(self.enckell)
        self.assertEqual(person.selibr, "185114")

    def test_get_ids(self):
        person = Person(self.enckell)
        ids = [{"type": "viaf", "value": "74098998"}, {
            "type": "isni", "value": "0000000051964492"}]
        self.assertEqual(person.auth_ids, ids)

    def test_get_ids_none(self):
        person = Person(self.strindberg)
        self.assertEqual(person.auth_ids, 0)

    def test_is_person_pass(self):
        personhood = process.is_person(self.enckell)
        self.assertTrue(personhood)

    def test_is_person_fail(self):
        personhood = process.is_person(self.organisation)
        self.assertFalse(personhood)

    def test_get_surname_1(self):
        person = Person(self.enckell)
        self.assertEqual(person.surname, "Enckell")

    def test_get_first_name(self):
        person = Person(self.enckell)
        self.assertEqual(person.first_name, "Martin")

    def test_get_descriptions_1(self):
        person = Person(self.enckell)
        desc = ["Finlandsvensk författare"]
        self.assertEqual(person.descriptions, desc)

    def test_get_dates_simple_living(self):
        dates = {"born": "1954", "dead": None}
        self.assertEqual(process.get_dates(self.enckell), dates)

    def test_get_dates_simple_dead(self):
        dates = {"born": "1838", "dead": "1920"}
        self.assertEqual(process.get_dates(self.runeberg), dates)

    def test_get_occupation_one(self):
        self.assertEqual(process.get_occupation(
            self.strindberg), ["författare"])

    def test_get_occupation_none(self):
        self.assertIsNone(process.get_occupation(self.enckell))


if __name__ == '__main__':
    unittest.main()
