import argparse
import json
import os
import re

# Make a collection for a year of Campus Publications (mvol) data. 
# For an example see: https://iiif-collection.lib.uchicago.edu/mvol/0004/mvol-0004-1930.json

#
# FUNCTIONS
#

def identifier_to_iiif_collection_url(identifier):
  """Build a uchicago IIIF collection URL for an mvol identifier. 
 
  Args:
    identifier (str): An mvol identifier, e.g. mvol-0004-1930

  Returns:
    str: An iiif-collection url, e.g. http://iiif-collection.lib.uchicago.edu/mvol/0004/mvol-0004-1930.json
 
  """

  pieces = identifier.split("-")
  if re.match(r"^mvol-\d{4}-\d{4}$", identifier) or re.match(r"^mvol-\d{4}-\d{4}-\d{2}$", identifier):
    return "http://iiif-collection.lib.uchicago.edu/" + "/".join(pieces[:2]) + "/" + identifier + ".json"
  else:
    raise ValueError

def get_year(identifier):
  """Get the year from an mvol identifier. 
 
  Args:
    identifier(str), e.g. mvol-0004-1930
  
  Returns:
    str: a year, e.g. 1930
 
  """

  return identifier.split("-")[2]

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

assert re.match(r"^mvol-\d{4}-\d{4}$", args.identifier)

year = get_year(args.identifier)

json_data = {
  'label': args.title + ', ' + '-'.join(args.identifier.split('-')[2:]),
  '@id': identifier_to_iiif_collection_url(args.identifier),
  '@context': 'https://iiif.io/api/presentation/2/context.json',
  '@type': 'sc:Collection',
  'description': args.description,
  'attribution': args.attribution,
  'viewingHint': 'multi-part',
  'members': []
}

months = set()
for entry in os.listdir(args.directory):
  if os.path.isdir(args.directory + "/" + entry) and re.match(r"^[0-9]{4}$", entry):
    months.add(entry[:2])
  
for month in sorted(list(months)):
  json_data['members'].append({
    'label': args.title + ', ' + year + '-' + month,
    '@id': identifier_to_iiif_collection_url(args.identifier + '-' + month),
    '@type': 'sc:Collection',
    'viewingHint': 'multi-part'
  })

print(json.dumps(json_data, indent=4, sort_keys=True))

