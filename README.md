# Digital Collection Validators

The University of Chicago Library assembles directories of image files,
metadata, OCR data, and more for digital project websites like [The Goodspeed
Manuscript Collection](https://goodspeed.lib.uchicago.edu), [The Speculum
Romanae Magnificentiae Digital Collection](http://speculum.lib.uchicago.edu),
and [The University of Chicago Photographic
Archive](photoarchive.lib.uchicago.edu).

These scripts validate, processes, and manages that data. They try to use fast
SSH connections for operations like read-only access, and they use WebDAV
access for write-access which helps keep the database in sync. 

These scripts are tightly coupled to the way that data is stored- you will have
to modify these scripts to use them in other contexts.

## Quickstart
```
docker build -t mvol_tools https://github.com/johnjung/mvol_tools.git
docker run --rm -it --env-file env.sh mvol_tools bash
```

## General Utility
digcoll is a general utility for working with digital collections data. You can
use it to report on files in the system.

How many directories are there for Speculum data?

```console
$ digcoll ls speculum | wc -l
      993
```

How many issues are there for each year of the Chicago Maroon? 

```console
$ ./digcoll ls mvol-0004 | cut -d '-' -f 3 | sort | uniq -c
  56 1902
 222 1903
 112 1904
 162 1905
 163 1906
 164 1907
 163 1908
 159 1909
 162 1910
 161 1911
 160 1912
 158 1913
 161 1914
 157 1915
 160 1916
 157 1917
 136 1918
 128 1919
...
```

## Campus Publications

### Validate directories
See what problems exist in a shipment of files.

```
mvol validate mvol-0004-1937
```

### Create a .dc.xml file on owncloud.
```
mvol put_dc_xml mvol-0004-1937-0105
```

### Regularize the name of the METS file in a given directory or directories.
This fixes filenaming errors for every issue in the year 1951. 

```
mvol regularize_mets mvol-0004-1951
```

### Regularize PDF filenames.
Fix filename errors for two different issues.

```
mvol regularize_pdf mvol-0004-1951-0105 mvol-0004-1951-0111
```

###

## check_sync
Check to see if files are 'in sync' between owncloud, the XTF development
server, and the XTF production server.


### Example
```
check_sync --owncloud-to-development mvol-0004-1937-0105
```

## mvol_sync
Check to see which directories are out of sync between owncloud, development
and production.

List all of the owncloud directories under "mvol". Show if they are valid, and
if files are present and in sync in dev and production.

```
python mvol_sync.py --list mvol
```

List all of the owncloud directories under "mvol-0004". Show if they are
valid, and if files are present and in sync in dev and production.

```
python mvol_sync.py --list mvol-0004
```

List all of the owncloud directories under "mvol-0004-0030". Show if they
are valid, and if files are present and in sync in dev and production.

```
python mvol_sync.py --list mvol-0004-0030
```

## put_struct_txt
Create or update a .struct.txt file on owncloud.

```
put_struct_txt mvol-0004-1937-0105
```

## Notes
You may need to modify this program to deal with SSH authentication issues.
Paramiko's connect() method can take an optional key_filename parameter to
identify an SSH key.

## Handy Shell Commands
```
find EWM -name "*.tif" -size 0
```

## See Also
+ [digital_collection_validators](https://github.com/uchicago-library/digital_collection_validators)
+ [mvol_script_dump](https://github.com/uchicago-library/mvol_script_dump)
