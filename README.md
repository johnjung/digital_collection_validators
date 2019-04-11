# mvol_tools

The Preservation department at the University of Chicago Library assembles
directories of files, including page images, metadata, and OCR data, to be
imported into websites like campub.lib.uchicago.edu.

This collection of scripts validates, processes, and manages those files. 

## Quickstart
```
docker build -t mvol_tools https://github.com/johnjung/mvol_tools.git
docker run --rm -it --env-file env.sh mvol_tools bash
```

## check_sync
Check to see if files are 'in sync' between owncloud, the XTF development
server, and the XTF production server.

### Example
```
check_sync --owncloud-to-development mvol-0004-1937-0105
```

## mvol ls
List mvol directories on owncloud that match certain patterns.

### Example
```
mvol ls mvol-0004-1937-0105
mvol ls mvol-0004-1937
mvol ls mvol-0004
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

## put_dc_xml
Create or update a .dc.xml file on owncloud.

```
put_dc_xml mvol-0004-1937-0105
put_dc_xml --force mvol-0004-1937-0105
```

## put_struct_txt
Create or update a .struct.txt file on owncloud.

```
put_struct_txt mvol-0004-1937-0105
```

## mvol validate
Checks to be sure directories of files on owncloud are valid.

```
mvol validate mvol-0004-1937-0105
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
