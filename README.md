# Biblioteksdata

Tools for the Library Data 2018–2019 project @ Wikimedia Sverige.

## Work with authority items using VIAF

`Biblioteksdata2/viaf.py` uses a data dump from [viaf.org](http://viaf.org/viaf/data/) (Txt file showing the correspondence between source IDs in clusters, e.g. *viaf-20210105-links.txt*) to add a VIAF ID based on the value a person item's Libris authority ID (SELIBR), and the other way round.

Usage:

To add VIAF ID's:

```
python3 viaf.py --path xxxxxxx.txt --action add_viaf_from_selibr
```

To add SELIBR ID's:

```
python3 viaf.py --path xxxxxxx.txt --action add_selibr_from_viaf
```

## Download and pre-process edition data

`Biblioteksdata2/harvester.py` downloads the metadata of a given edition, or set of editions, from Libris and pre-processes it for further work e.g. in OpenRefine. The bulk of the data, which is not relevant for Wikidata, is removed, and the remaining parts are simplified so that the output is human-readable.

Usage:

```
python3 harvester.py --book xxxxxxx -out books.json
```

Flags:
* `--book` process a single entry, using either old Edition ID or URI (will be detected automatically)
* `--list` process a file containing a list of identifiers (either old Edition ID or URI's), one per line
* `--out` specify filename of the output

## Download results of xsearch search

`Biblioteksdata2/xsearch.py` performs a search in the Libris API using [xsearch codes](http://librishelp.libris.kb.se/help/search_codes_swe.jsp).

Usage:

```
python3 xsearch.py --query "db:natbib AND mat:eresurser AND mat:bok" --file eresurser
```

This will download the results [of this API call](http://libris.kb.se/xsearch?query=db:natbib%20AND%20mat:eresurser&format=json) (looping over the pagination, so all the results) and save them in the file `eresurser.json`.


## Import of Libris edition posts

`process_edition.py` is for uploading data about Libris editions.

When importing a post, the script will attempt to locate an existing Wikidata item using the Libris identifiers (URI or Libris edition) as well as ISBN numbers. If a matching item is identified, the data will be added to it. Otherwise a new item will be created.

Note that `Edition.py` checks whether the Libris post is tagged as belonging to the Swedish National Bibliography. Posts that are not will not be imported to Wikidata.

In order to upload the data to Wikidata (as opposed to only processing the data), use the `upload` flag:

`--upload` – upload changes to Wikidata, either to a `sandbox` or `live`

There are two ways to import edition posts from Libris to Wikidata.

### Import a single edition using the API

This will import a single edition's data. You have to give the URI of the edition:

`--uri` – find and process single file with specific Libris URI

For example:

```
python3 process_edition.py --upload live --uri r8224c130tmvk2h
```

### Import of several posts from local database dump

This mode was designed to work specificaly with the Swedish National Bibliography dump we received from the National Library. The dump is a directory of json-ld files.

Here, the input must be a file of SELIBR ID's (old style), one per line.

Use the following flags:

`--dir` – location of the data directory
`--source_selibr` – location of file with SELIBR ID's

## Import of authorities

* **importer/process_auth.py** – taking a directory of Libris authority posts (one json-ld object per file), match with Wikidata items with corresponding Selibr ID's and add Libris URI to it.

Options:

`--limit` – only process the first x files in the directory

```
python3 importer/process_auth.py --dir librisfiles/ --limit 1000 --upload live
```

## Data pre-processing

The pre-processing scripts take the data from https://figshare.com/articles/Wikipedia_Scholarly_Article_Citations/1299540 and generate frequency lists for *ISBN* works and their authors (using the Libris database).

* **process_refs/counter.py** – create a TSV file of ISBN:count pairs. Takes a citation dump as input. [Output for svwp](https://gist.github.com/Vesihiisi/4dae5b0b52c93cd7d94741acbf395754)

```
python3 counter.py --path svwiki.tsv
```

* **process_refs/process_isbn_refs.py** – using the Libris API, convert the ISBN frequency list to titles and authors. Can be limited to n top entries. Wikidata matches for works will be found via ISBN and Libris ID. [Output for svwp – works](https://gist.github.com/Vesihiisi/04ec2c73a774b7a33b48de62143fe62c). [Output for svwp – authors](https://gist.github.com/Vesihiisi/0dd90db206bbe86ad2f502781365fa28).

```
python3 process_refs.py --path isbn_sorted.tsv --limit 20
```

* **process_refs/process_runeberg.py** – create a frequency count for the runeberg.org template with different parameters on svwp. [Output](https://gist.github.com/Vesihiisi/4ed15b89a5a5c316398adea5b165625f).

* **process_refs/process_all_refs.py** create a frequency count for the bokref template and URL's on svwp. [Output – bookrefs](https://gist.github.com/Vesihiisi/400529978ad1757db9b096ff1ee6545a). [Output – URL's](https://gist.github.com/Vesihiisi/1a47ea5cbf1d8532f8a4469b74e9c121)

## Runeberg scraper
`runeberg/process_catalog.py` scrapes the catalog of Project Runeberg (http://runeberg.org/katalog.html) into a structured Json file. It also attempts to get the Q-ID's of matching Wikidata items of editions (via Libris ID's) and authors. An item in the output looks like this:

```
{
    "material": "book",
    "libris": "232520",
    "title": {
        "work_id": "drottningh",
        "work_title": "Drottningholm. Dess historia, samlingar och närmaste omgifningar"
    },
    "authors": [
        {
            "author_id": "carlenoc",
            "author_name": "Carlén, Octavia",
            "wikidata": "Q4941855"
        }
    ],
    "date": "1861",
    "language": "se",
    "wikidata": "Q65525330"
}
```