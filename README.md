# Biblioteksdata

Tools for the Library Data 2018 project @ Wikimedia Sverige.

## Import of Libris URI's

* **importer/process_auth.py** – taking a single New Libris Authority post, either in a local file or online, match with a Wikidata item with a corresponding Selibr ID and add Libris URI to it.

```
python3 importer/process_auth.py --uri xxxxxx --upload live
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

* **process_refs/process_all_refs.py** create a frequency count for the bokref template on svwp. [Output](https://gist.github.com/Vesihiisi/400529978ad1757db9b096ff1ee6545a).