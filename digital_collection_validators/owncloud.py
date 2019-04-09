import stat
import sys


class FilesystemTools:
  mappings = {
    'maps': {
      'input': {
        'pi.lib.uchicago.edu': r'^http://pi\.lib\.uchicago\.edu/1001/([^/]*)/([^/]*)/(.*)$'
      }
      'output': {
        'identifier':          r'\3',
        'owncloud':            r'^data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/maps/\1/\2/\3',
      }
    },
    'mvol': {
      'input': {
        'identifier':          r'^mvol-(\d{4})-(\d{4})-(\d{4})$'
      }
      'output': {
        'owncloud':            r'/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/mvol-\1-\2-\3',
        'xtf_development':     r'/usr/local/apache-tomcat-6.0/webapps/xtf/data/bookreader/mvol-\1-\2-\3',
        'xtf_production':      r'/usr/local/apache-tomcat-6.0/webapps/campub/data/bookreader/mvol-\1-\2-\3'
      }
    }
  }

  # python regular expression search and replace. 
  # re.sub(r'\* \[(.*)\]\(#(.*)\)', r'<h2 id="\2">\1</h2>', line.rstrip())
   
   

  def get_newest_modification_time_from_directory(ftp, directory):
    """ Helper function for get_newest_modification_time. Recursively searches
    subdirectories for the newest modification time. 
     
    :param ftp: paramiko ftp instance
    :param str directory: path to an identifier's files on disk, on either
    owncloud or one of the XTF servers.

    :returns the newest unix timestamp present in that directory.
    """

    mtimes = []
    for entry in ftp.listdir_attr(directory):
      if stat.S_ISDIR(entry.st_mode):
        mtime = get_newest_modification_time_from_directory(ftp, '{}/{}'.format(directory, entry.filename))
      else:
        try:
          mtimes.append(entry.st_mtime)
        except FileNotFoundError:
          sys.stderr.write(directory + '\n')
          raise FileNotFoundError

    if mtimes:
      return max(mtimes)
    else:
      return 0


  def get_newest_modification_time(ftp, path_function, identifier):
    """Get the most recent modification time for the files associated with a given identifier. 
 
    :param ftp: paramiko ftp instance
    :param path_function: one of get_path_owncloud, get_path_xtf_development,
                          get_path_xtf_production
    :param str identifier: e.g. 'mvol-0001-0002-0003'

    :returns the newest unix timestamp present in that directory.
    """
    return get_newest_modification_time_from_directory(ftp, path_function(identifier))


  def get_path_owncloud(identifier):
    """Return a path for a given identifier on owncloud's filesystem.

    :param str identifier: e.g. 'mvol-0001-0002-0003'

    :rtype str
    :returns the path to this file on owncloud's filesystem. Note that you
    should use these paths for read access only.
    """

    return '/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/{}'.format(identifier.replace('-', '/'))


  def get_path_xtf_development(identifier):
    """Return a path for a given identifier on the XTF development server's filesystem.

    :param str identifier: e.g. 'mvol-0001-0002-0003'

    :rtype str
    :returns the path to this file on XTF's filesystem.
    """
    return '/usr/local/apache-tomcat-6.0/webapps/xtf/data/bookreader/{}'.format(identifier)


  def get_path_xtf_production(identifier):
    """Return a path for a given identifier on the XTF production server's filesystem.

    :param str identifier: e.g. 'mvol-0001-0002-0003'

    :rtype str
    :returns the path to this file on XTF's filesystem.
    """
    return '/usr/local/apache-tomcat-6.0/webapps/campub/data/bookreader/{}'.format(identifier)
