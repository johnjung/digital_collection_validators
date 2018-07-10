import argparse
import json
import os
import re   

from mvol_identifier import MvolIdentifier

class IIIFManifest:
  """Make a manifest for a Campus Publications (mvol) issue.
     e.g. https://iiif-manifest.lib.uchicago.edu/mvol/0004/1929/0103/mvol-0004-1929-0103.json

  """

  def __init__(self, title, identifier, description, attribution, directory):

    self.title = title
    self.identifier = identifier
    self.description = description
    self.attribution = attribution
    self.directory = directory

    self.mvolidentifier = MvolIdentifier(self.identifier)
    self.year = self.mvolidentifier.get_year()

  def data(self):

    manifest = {
      '@context': 'http://iiif.io/api/presentation/2/context.json',
      '@id': self.mvolidentifier.manifest_url(),
      '@type': 'sc:Manifest',
      'metadata': [
        {
          'label': 'Title',
          'value': self.title
        },
        {
          'label': 'Identifier',
          'value': self.identifier
        },
        {
          'label': 'Date',
          'value': self.mvolidentifier.get_year_month_date()
        }
      ],
      'description': self.description,
      'logo': 'https://www.lib.uchicago.edu/static/base/images/color-logo.png',
      'license': 'http://campub.lib.uchicago.edu/rights/',
      'attribution': 'University of Chicago Library',
      'label': self.title + ', ' + self.mvolidentifier.get_year_month_date(),
      'sequences': [
        {
          '@id': self.mvolidentifier.sequence_url(),
          '@type': 'sc:Sequence',
          'canvases': [],
        }
      ],
      'structures': [],
      'viewingDirection': 'left-to-right'
    }

    for e, entry in enumerate(os.listdir(self.directory)):
       manifest['sequences'][0]['canvases'].append({
        '@id': self.mvolidentifier.sequence_url(),
        '@type': 'sc:Canvas',
        'label': get_page(e),
        'height': get_height(e),
        'width': get_width(e),
        'images': [
          {
            '@context': 'http://iiif.io/api/presentation/2/context.json',
            '@id': 'some url',
            '@type': 'oa:Annotation',
            'motivation': 'sc:Painting',
            'resource': {
              '@id': 'http://iiif-server.lib.uchicago.edu/mvol%2F0004%2F1929%2F0103%2FTIFF%2Fmvol-0004-1929-0103_0001.tif/full/full/0/default.jpg',
              '@type': 'dctypes:Image',
              'format': 'image/jpeg??????',
              'height': get_height(e),
              'width': get_width(e),
              'service': {
                '@context': 'http://iiif.io/api/image/2/context.json',
                '@id': 'https://iiif-server.lib.uchicago.edu/mvol%2F0004%2F1929%2F0103%2FTIFF%2Fmvol-0004-1929-0103_0001.tif',
                'profile': [
                   'http://iiif.io/api/image/2/level2.json',
                   {
                     'supports': [
                        'canonicalLinkHeader',
                        'profileLinkHeader',
                        'mirroring',
                        'rotationArbitrary',
                        'regionSquare',
                        'sizeAboveFull'
                     ],
                     'qualities': [
                       'default',
                       'gray',
                       'bitonal'
                     ],
                     'format': [
                       'jpg',
                       'png',
                       'gif',
                       'webp'
                      ]
                   }
                ]
              }
            },
            'on': this.mvolidentifier.get_sequence_url()
          }
        ]
      })

    return manifest

if __name__ == '__main__':

  def mvol_year_month_date(s):
    r = re.compile(r"^mvol-\d{4}-\d{4}-\d{4}$")
    if not r.match(s):
      raise argparse.ArgumentTypeError
    return s

  parser = argparse.ArgumentParser()
  parser.add_argument("identifier", help="e.g. mvol-0004-1931", type=mvol_year_month_date)
  parser.add_argument("directory", help="e.g. /Volumes/webdav/...")
  args = parser.parse_args()

  if args.identifier.startswith('mvol-0004'):
    title = 'Daily Maroon'
    description = 'A newspaper produced by students of the University of Chicago published 1900-1942 and continued by the Chicago Maroon.'
  else:
    raise NotImplementedError

  print(
    json.dumps(
      IIIFManifest(
        title,
        args.identifier,
        description,
        'University of Chicago Library',
        args.directory).data(),
      indent=4,
      sort_keys=True))
