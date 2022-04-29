import csv
import requests
import sys
from openpyxl import Workbook
from pathlib import Path
from time import sleep
from xml.etree import ElementTree

def main(filename):
  csv_data = csv_generator(filename)
  organisms = read_first_column(csv_data)
  organisms = clean_organisms(organisms)
  ids = fetch_ids(organisms, fetch_from_ncbi)
  outfile = create_outfile_name(filename)
  write_ids(ids, outfile)

def csv_generator(filename):
  '''
  Generator for CSV files.

  Yields a list of rows after skipping the header.
  '''
  with open(filename, 'r') as f:
    reader = csv.reader(f)
    next(reader)
    yield from reader

def read_first_column(csv_data):
  '''
  Read the first column of a CSV file, passed as a generator, and return a list of strings.

  Strip any surrounding whitespace to account for entry errors.
  '''
  return [row[0].strip() for row in csv_data]

def clean_organisms(organisms):
  '''
  Clean up organism names for searching.

  Remove: newlines, "spp." and "spp". Clean up duplicated spaces.
  '''
  result = []
  for organism in organisms:
    organism = organism.replace('\n', ' ')
    organism = ' '.join(organism.split())
    if organism.endswith(' spp.'):
      organism = organism[:-5]
    if organism.endswith(' spp'):
      organism = organism[:-4]
    result.append(organism)
  return result

def fetch_ids(organisms, fetch):
  '''
  Fetch the taxon IDs for a list of organisms.

  Rate limit is 10 requests per second. Using 0.2 seconds between requests to
  be safe.
  '''
  result = {
    'failed': [],
    'mapped': {},
  }
  for organism in organisms:
    if document := fetch(organism):
      taxon_id = document.find('IdList').find('Id')
      if taxon_id is not None:
        result['mapped'][organism] = int(taxon_id.text)
      else:
        result['failed'].append(organism)
    else:
      result['failed'].append(organism)
    sleep(0.2)
  return result

def fetch_from_ncbi(organism):
  '''
  Query NCBI's taxonomy database for a given organism, returning XML.
  '''
  url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&term={organism}'
  r = requests.get(url)
  return ElementTree.fromstring(r.text) if r.status_code == 200 else None

def create_outfile_name(filename):
  '''
  Create an output file name based on the input file name.

  It will write to the same directory as the input file, and append "_output.xlsx".
  '''
  file = Path(filename)
  return str(file.parent / f'{file.stem}_out.xlsx')

def write_ids(ids, filename):
  '''
  Write the mapped taxon IDs to an Excel file.

  The first sheet contains the mapping of organisms to taxon IDs.
  The second sheet is used for listing the failed organisms.
  '''
  wb = Workbook()
  ws = wb.active
  ws.title = 'Mapping'
  ws.append(['Organism', 'Taxon ID'])
  for organism, taxon_id in ids['mapped'].items():
    ws.append([organism, taxon_id])
  ws = wb.create_sheet('Failed')
  ws.append(['Organism'])
  for organism in ids['failed']:
    ws.append([organism])
  wb.save(filename)

if __name__ == '__main__':
  argv = sys.argv
  if len(argv) != 2:
    print(f'Usage: python3 {argv[0]} <filename>')
    sys.exit(1)
  main(argv[1])
