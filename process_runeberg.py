#!/usr/bin/python
# -*- coding: utf-8  -*-
from collections import Counter
import mwparserfromhell as parser
import pywikibot as pwb
from pywikibot import pagegenerators as pg

TEMPLATE = "runeberg.org"
OUTPUT = "runeberg_sorted.tsv"


def save_sorted(sorted_data, fname):
    """Save sorted  data as tsv file."""
    with open(fname, "w") as f:
        for k, v in sorted_data:
            f.write("{}\t{}\n".format(k, v))
    print("Saved file: {}".format(OUTPUT))


def get_template_usage(article, template):
    usages = []
    page_str = parser.parse(article.get())
    templates = page_str.filter_templates()
    for t in templates:
        if t.name.matches(template):
            useful_parts = []
            for part in t.split("|"):
                if all(s not in part for s in ["{{", "}}", 'html']):
                    useful_parts.append(part)
            usages.append("|".join(useful_parts))
    return usages


def get_template_generator(lng, tpl):
    site = pwb.Site(lng, "wikipedia")
    tpl = "runeberg.org"
    tpl_name = "{}:{}".format(site.namespace(10), tpl)
    tpl_page = pwb.Page(site, tpl_name)
    ref_gen = pg.ReferringPageGenerator(tpl_page, onlyTemplateInclusion=True)
    filter_gen = pg.NamespaceFilterPageGenerator(ref_gen, namespaces=[0])
    return site.preloadpages(filter_gen, pageprops=True)


def main():
    all_usages = []
    gen = get_template_generator("sv", TEMPLATE)
    for article in gen:
        all_usages.extend(get_template_usage(article, TEMPLATE))
        commonest = Counter(all_usages).most_common()
    save_sorted(commonest, OUTPUT)


if __name__ == "__main__":
    main()
