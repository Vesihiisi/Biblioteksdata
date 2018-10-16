#!/usr/bin/python
# -*- coding: utf-8  -*-
import argparse
import os
import pywikibot
import importer_utils as utils

import importer_utils as utils
from Edition import Edition
from Uploader import Uploader


def main():
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("--dir", required=True)
    parser.add_argument("--uri")
    parser.add_argument("--upload", action='store')
    parser.add_argument("--limit",
                        nargs='?',
                        type=int,
                        action='store')
    args = parser.parse_args()
    main(vars(args))
