# Fetch taxon IDs

Given a CSV file with a list of organisms in the first column, fetch the NCBI taxon ID for each organism.

The CSV file is assumed to have a header. A small amount of clean up is done on organism names to make them more suitable for NCBI queries. Extraneous spaces are removed, and suffixes "spp." and "spp" are removed.

NCBI has a rate limit of 10 requests per second, so this script will attempt 5 requests per second. For 100 organisms, expect it to take ~20 seconds.

## Usage

```
python fetch_taxon_ids.py file.csv
```

## Output

Output will be written as an xlsx file to the same directory where the input file is located. The file is named after the input file as `<file>_out.xlsx`.

It will contain two sheets, the first with a two-column list of mapped organisms, and the second with a list of organisms that could not be mapped.

## Tests

```
pytest test_fetch_taxon_ids.py
```
