import csv
import os
import sys
import xml.etree.cElementTree as ET

# input- an identifier as a string, e.g.:
#   mvol-0004-1931-0106
# output- a filesystem path as a string, e.g.:
#   /Volumes/webdav/IIIF_Files/mvol/0004/1931/0106/
def get_path(identifier):
  return '/Volumes/webdav/IIIF_Files/' + '/'.join(identifier.split('-')) + '/'

# input- an identifier as a string, e.g.:
#   mvol-0004-1931-0106
# output- a .dc.xml filename, e.g.:
#   mvol-0004-1931-0106.dc.xml
def get_filename(identifier):
  return identifier + '.dc.xml'

# the script takes a .csv file as a parameter.

with open(sys.argv[1]) as input_f:
  reader = csv.reader(input_f, delimiter=',')

  # skip header
  next(reader, None)

  for row in reader:
    # be sure the directory exists. 
    assert os.path.exists(get_path(row[2]))

    # be sure the file does not exist.
    assert os.path.isfile(get_path(row[2]) + get_filename(row[2])) == False

    print(row[2])

    metadata = ET.Element('metadata')
    ET.SubElement(metadata, 'title').text = row[0]
    ET.SubElement(metadata, 'date').text = row[1]
    ET.SubElement(metadata, 'description').text = row[3]
    ET.SubElement(metadata, 'identifier').text = row[2]

    with open(get_path(row[2]) + get_filename(row[2]), 'w') as output_f:
      output_f.write(ET.tostring(metadata, encoding='utf8', method='xml').decode('utf8'))
  
