import argparse
import json
import os
import re

#
# FUNCTIONS
#

def identifier_to_iiif_collection_url(identifier):
  """Build a uchicago IIIF collection URL for an mvol identifier. 
 
  Args:
    identifier (str): An mvol identifier, e.g. mvol-0004-1930-01

  Returns:
    str: An iiif-collection url, e.g. http://iiif-collection.lib.uchicago.edu/mvol/0004/mvol-0004-1930-01.json
 
  """

  pieces = identifier.split("-")
  if re.match(r"^mvol-[0-9]{4}-[0-9]{4}-[0-9]{2}$", identifier):
    return "http://iiif-collection.lib.uchicago.edu/" + "/".join(pieces[:2]) + "/" + identifier + ".json"
  else:
    raise ValueError

def identifier_to_iiif_manifest_url(identifier):
  """Build a uchicago IIIF manifest URL for an mvol identifier. 
 
  Args:
    identifier (str): An mvol identifier, e.g. mvol-0004-1930-0103

  Returns:
    str: An iiif-collection url, e.g. http://iiif-manifest.lib.uchicago.edu/mvol/0004/1930/0103/mvol-0004-1930-0103.json
 
  """

  pieces = identifier.split("-")
  if re.match(r"^mvol-[0-9]{4}-[0-9]{4}-[0-9]{4}$", identifier):
    return "http://iiif-manifest.lib.uchicago.edu/" + "/".join(pieces) + "/" + identifier + ".json"

def get_year(identifier):
  """Get the year from an mvol identifier. 
 
  Args:
    identifier(str), e.g. mvol-0004-1930
  
  Returns:
    str: a year, e.g. 1930
 
  """

  return identifier.split("-")[2]

def get_month(identifier):
  """Get the month from an mvol identifier. 
 
  Args:
    identifier(str), e.g. mvol-0004-1930-01
    identifier(str), e.g. mvol-0004-1930-0106
  
  Returns:
    str: a month, e.g. 01
 
  """

  return identifier.split("-")[3][:2]

def get_date(identifier):
  """Get the month from an mvol identifier. 
 
  Args:
    identifier(str), e.g. mvol-0004-1930-0106
  
  Returns:
    str: a date, e.g. 06
 
  """

  return identifier.split("-")[3][2:]

def get_year_month_date(identifier):
  """Get the year-month-date from an identifier. 
 
  Args:
    identifier(str), e.g. mvol-0004-1930-0106
  
  Returns:
    str: a date, e.g. 1930-01-06
 
  """

  return get_year(identifier) + '-' + get_month(identifier) + '-' + get_date(identifier)

#
# MAIN
#

parser = argparse.ArgumentParser()
parser.add_argument("directory", help="e.g. /Volumes/webdav/...")
parser.add_argument("title", help="e.g. Daily Maroon")
parser.add_argument("identifier", help="e.g. mvol-0004-1931")
parser.add_argument("description", help="e.g. A newspaper produced by students of the University of Chicago. Published 1900-1942 and continued by the Chicago Maroon.")
parser.add_argument("attribution", help="e.g. University of Chicago")
args = parser.parse_args()

assert re.match(r"^mvol-\d{4}-\d{4}-\d{2}$", args.identifier)

year = get_year(args.identifier)
month = get_month(args.identifier)

json_data = {
  'label': args.title + ', ' + '-'.join(args.identifier.split('-')[2:]),
  '@id': identifier_to_iiif_collection_url(args.identifier),
  '@context': 'https://iiif.io/api/presentation/2/context.json',
  '@type': 'sc:Collection',
  'description': args.description,
  'attribution': args.attribution,
  'viewingHint': 'individuals',
  'members': []
}

for entry in os.listdir(args.directory):
  if os.path.isdir(args.directory + "/" + entry) and re.match(r"^\d{4}$", entry):
    entry_identifier = '-'.join(args.identifier.split('-')[:3]) + '-' + entry
    if get_month(entry_identifier) == month:
      json_data['members'].append({
        'label': args.title + ', ' + get_year_month_date(entry_identifier),
        '@id': identifier_to_iiif_manifest_url(entry_identifier),
        '@type': 'sc:Manifest',
        'viewingHint': 'individuals'
      })

print(json.dumps(json_data, indent=4, sort_keys=True))

