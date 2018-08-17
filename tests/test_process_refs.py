#!/usr/bin/python
# -*- coding: utf-8  -*-
import unittest
import importer.process_refs as process


class TestLibrisAPI(unittest.TestCase):
    """Tests for dictionary manipulations."""

    def test_download_data(self):
        isbn = "9780226894089"
        self.assertEqual(len(process.download_data(isbn)), 1)


if __name__ == '__main__':
    unittest.main()
