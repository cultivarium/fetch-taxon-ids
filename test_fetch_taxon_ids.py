from xml.etree import ElementTree
import pytest

from fetch_taxon_ids import clean_organisms, create_outfile_name, csv_generator, fetch_ids, read_first_column

class TestCsvGenerator:
  def test(self, tmp_path):
    file = tmp_path / 'test.csv'
    file.write_text('Species,Alternative Names\nAquifex pyrophilus,-\n')
    
    expected = ['Aquifex pyrophilus', '-']
    csv_data = csv_generator(file)
    assert next(csv_data) == expected

class TestReadFirstColumn:
  def test(self):
    def generator():
      yield ['Aquifex pyrophilus', 'Other field']
      yield ['Pseudozyma spp. ', 'Other field']
    expected = ['Aquifex pyrophilus', 'Pseudozyma spp.']
    assert read_first_column(generator()) == expected

class TestCleanOrganisms:
  def test(self):
    organisms = [
      'Aquifex pyrophilus',
      'Pseudozyma spp.',
      'Sporobolomyces spp',
      'Streptomyces\ncoelicolor',
      'Streptomyces  sodiiphilus',
    ]
    expected = [
      'Aquifex pyrophilus',
      'Pseudozyma',
      'Sporobolomyces',
      'Streptomyces coelicolor',
      'Streptomyces sodiiphilus',
    ]
    assert clean_organisms(organisms) == expected

class TestFetchIds:
  def test(self):
    def fetch(organism):
      if organism == 'Aquifex pyrophilus':
        return ElementTree.fromstring('<eSearchResult><IdList><Id>2714</Id></IdList></eSearchResult>')
      if organism == 'Bacillus clausii C360':
        return ElementTree.fromstring('<eSearchResult><IdList/></eSearchResult>')
      return None
    organisms = ['Aquifex pyrophilus', 'Bacillus clausii C360', 'Pseudozyma']
    expected = {
      'failed': ['Bacillus clausii C360', 'Pseudozyma'],
      'mapped': {
        'Aquifex pyrophilus': 2714,
      },
    }
    assert fetch_ids(organisms, fetch) == expected

class TestCreateOutfileName:
  def test(self):
    infile = 'data/test.csv'
    expected = 'data/test_out.xlsx'
    assert create_outfile_name(infile) == expected