#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Process the Runeberg.org catalog
"""
from bs4 import BeautifulSoup

CATALOG = "runeberg_catalog_2018-09-18.html"


def process_material(raw):
    alts = [img['alt'] for img in raw.find_all('img', alt=True)]
    if len(alts) == 1:
        return alts[0].lower()


def process_title(raw):
    tags = raw.find_all('a')
    if len(tags) == 1:
        title_dict = {}
        href = tags[0].get("href")
        title_dict["work_id"] = href.replace("/", "")
        title_dict["work_title"] = tags[0].contents[0]
        return title_dict


def process_marc(raw):
    tags = raw.find_all('a')
    if len(tags) > 0:
        for tag in tags:
            href = tag.get("href")
            if "libris.kb.se/bib" in href:
                return href.split("/")[-1]


def process_authors(raw):
    authors = []
    tags = raw.find_all('a')
    if len(tags) > 0:
        for tag in tags:
            author_dict = {}
            author_dict["author_id"] = tag.get(
                'href').split("/")[-1].split(".")[0]
            author_dict["author_name"] = tag.contents[0]
            authors.append(author_dict)
    return authors


def process_language(raw):
    alts = [img['alt'] for img in raw.find_all('img', alt=True)]
    if len(alts) == 1:
        return alts[0]


def process_date(raw):
    return raw.text


def process_work(row):
    cells = row.findAll('td')
    work = {
        "material": process_material(cells[0]),
        "libris": process_marc(cells[2]),
        "title": process_title(cells[4]),
        "authors": process_authors(cells[6]),
        "date": process_date(cells[8]),
        "language": process_language(cells[10])
    }
    return work


def main():
    f = open(CATALOG, "r")
    soup = BeautifulSoup(f.read(), "html.parser")
    table_of_contents = soup.findAll("table")[0]
    rows = table_of_contents.find_all('tr')
    for row in rows:
        work = process_work(row)
        print(work)


if __name__ == "__main__":
    main()
