#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Examine runeberg.org templates on svwp.

This generates a frequency list of runeberg.org
templates with different parameters
on Swedish Wikipedia.
"""
from collections import Counter
from pywikibot import pagegenerators as pg
import mwparserfromhell as parser
import pywikibot as pwb

TEMPLATE = "runeberg.org"
OUTPUT = "runeberg_sorted.tsv"


def save_sorted(sorted_data, fname):
    """Save sorted  data as tsv file."""
    with open(fname, "w") as f:
        f.write("{}\t{}\n".format("path", "count"))
        for k, v in sorted_data:
            f.write("{}\t{}\n".format(k, v))
    print("Saved file: {}".format(OUTPUT))


def get_template_usage(article, template):
    """
    List all usages of runeberg template in article.

    Some of them have single parameters like
    "nfbk" and others have two like "vemardet|1969",
    both variants are accommodated.
    If the template is malformed, it's not
    counted – about 75 in svwp, so not statistically
    significant.
    Examples:
    {{runeberg.org|nfbj|0368.html Gustaf III}} → nfbj
    {{runeberg.org|vemardet|1977|0513.html Jansson, Alvar}} → vemardet|1977

    """
    usages = []
    page_str = parser.parse(article.get())
    templates = page_str.filter_templates()
    for t in templates:
        if t.name.matches(template):
            useful_parts = []
            for part in t.split("|"):
                if all(s not in part for s in ["{{", "}}", 'html']):
                    useful_parts.append(part)
            usage = "|".join(useful_parts)
            if len(usage) > 0:
                usages.append(usage)
    return usages


def get_template_generator(lng, tpl):
    """Create a generator of articles linking to template."""
    site = pwb.Site(lng, "wikipedia")
    tpl_name = "{}:{}".format(site.namespace(10), tpl)
    tpl_page = pwb.Page(site, tpl_name)
    ref_gen = pg.ReferringPageGenerator(tpl_page, onlyTemplateInclusion=True)
    filter_gen = pg.NamespaceFilterPageGenerator(ref_gen, namespaces=[0])
    return site.preloadpages(filter_gen, pageprops=True)


def process_all():
    """Generate a frequency list from svwp."""
    all_usages = []
    gen = get_template_generator("sv", TEMPLATE)
    for article in gen:
        all_usages.extend(get_template_usage(article, TEMPLATE))
        commonest = Counter(all_usages).most_common()
    save_sorted(commonest, OUTPUT)


if __name__ == "__main__":
    process_all()
