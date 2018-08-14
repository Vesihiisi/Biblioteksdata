#!/usr/bin/python
# -*- coding: utf-8  -*-
import unittest
import importer.process_auth as process


class TestAuthProcessing(unittest.TestCase):

    def setUp(self):
        self.strindberg = process.get_from_uri("tr574vdc33gk2cc")
        self.enckell = process.get_from_uri("xv8bb94g23ng552")

    def test_is_person(self):
        personhood = process.is_person(self.enckell)
        self.assertTrue(personhood)

    def test_get_surname_1(self):
        surname = process.get_surname(self.enckell)
        self.assertEqual(surname, "Enckell")


if __name__ == '__main__':
    unittest.main()
