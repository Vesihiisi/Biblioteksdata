#!/usr/bin/python
# -*- coding: utf-8  -*-
import unittest
import importer.process_auth as process


class TestAuthProcessing(unittest.TestCase):

    def setUp(self):
        self.strindberg = process.get_from_uri("tr574vdc33gk2cc")
        self.enckell = process.get_from_uri("xv8bb94g23ng552")
        self.organisation = process.get_from_uri("64jljffq17m41sr")

    def test_get_selibr(self):
        selibr = process.get_selibr(self.enckell)
        self.assertEqual(selibr, "185114")

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


if __name__ == '__main__':
    unittest.main()
