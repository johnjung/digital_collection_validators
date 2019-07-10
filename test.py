import io
import unittest
from digital_collection_validators.classes import OwnCloudSSH, OwnCloudWebDAV
from pathlib import Path


class TestSSH(unittest.TestCase):
    def test_is_identifier(self):
	""" Be sure that identifiers conform to their filenaming spec. Note
	that this function does not need to confirm that an identifier with
	that name currently exists- it only needs to confirm that an identifier
        with that name would be legal.
        """
        # "apf"        is not an identifier. 
        # "apf1"       is not an identifier.
        # "apfx"       is not an identifier.
        # "apf1-"      is not an identifier.
        # "apf1-00001" is an identifier.
        # "apf1-0001"  is not an identifier.
        # "apf1-a"     is not an identifier.

        # "chopin"     is not an identifier. 
        # "chopin-"    is not an identifier. 
        # "chopin-001" is an identifier. 
        # "chopin-abc" is not an identifier. 

        # "ewm"        is not an identifier.
        # "ewm-"       is not an identifier.
        # "ewm-0001"   is an identifier. 
        # "ewm-abcd"   is not an identifier. 

        # "gms"        is not an identifier. 
        # "gms-"       is not an identifier. 
        # "gms-0001"   is an identifier. 
        # "gms-abcd"   is not an identifier. 

        # "mvol"                 is not an identifier.
        # "mvol-"                is not an identifier
        # "mvol-0001"            is not an identifier
        # "mvol-0001-"           is not an identifier
        # "mvol-0001-0002"       is not an identifier
        # "mvol-0001-0002-"      is not an identifier
        # "mvol-0001-0002-0003"  is an identifier

        # "speculum"             is not an identifier.
        # "speculum-0001"        is an identifier.
        raise NotImplementedError

    def test_is_identifier_chunk(self):
	""" Be sure that identifier chunks conform to their filenaming spec. Note
	that this function does not need to confirm that an identifier chunk with
	that name currently exists- it only needs to confirm that one with that
        name would be legal.
        """
        # "apf"        is an identifier chunk. 
        # "apf1"       is an identifier chunk.
        # "apfx"       is not an identifier chunk.
        # "apf1-"      is not an identifier chunk.
        # "apf1-00001" is an identifier chunk.
        # "apf1-0001"  is not an identifier chunk.
        # "apf1-a"     is not an identifier chunk.

        # "chopin"     is an identifier chunk. 
        # "chopin-"    is not an identifier chunk. 
        # "chopin-001" is an identifier chunk. 
        # "chopin-abc" is not an identifier chunk. 

        # "ewm"        is an identifier chunk.
        # "ewm-"       is not an identifier chunk.
        # "ewm-0001"   is an identifier chunk. 
        # "ewm-abcd"   is not an identifier chunk. 

        # "gms"        is an identifier chunk. 
        # "gms-"       is not an identifier chunk. 
        # "gms-0001"   is an identifier chunk. 
        # "gms-abcd"   is not an identifier chunk. 

        # "mvol"                 is an identifier chunk.
        # "mvol-"                is not an identifier chunk
        # "mvol-0001"            is an identifier chunk
        # "mvol-0001-"           is not an identifier chunk
        # "mvol-0001-0002"       is an identifier chunk
        # "mvol-0001-0002-"      is not an identifier chunk
        # "mvol-0001-0002-0003"  is an identifier chunk

        # "speculum"             is an identifier chunk.
        # "speculum-0001"        is an identifier chunk.
        raise NotImplementedError


class TestMvolValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owncloud = OwnCloudSSH()

    def test_struct_txt_has_headers(self):
        """struct.txt validator requires headers."""
        with io.StringIO('00000001\t1\n'
                         '00000002\t2\n'
                         '00000003\t3\n'
                         '00000004\t4') as f:
            self.assertTrue(
                len(self.owncloud.validate_struct_txt('mvol-0001-0002-0003', f)) > 0
            )

    def test_struct_txt_has_commas(self):
        """struct.txt validator requires headers."""
        with io.StringIO('object,page,milestone\n'
                         '00000002,2,\n'
                         '00000003,3,\n'
                         '00000004,4,') as f:
            self.assertTrue(
                len(self.owncloud.validate_struct_txt('mvol-0001-0002-0003', f)) > 0
            )

    def test_struct_txt_has_tabs(self):
        """struct.txt validator requires headers."""
        with io.StringIO('object\tpage\tmilestone\n'
                         '00000002\t2\n'
                         '00000003\t3\n'
                         '00000004\t4') as f:
            self.assertEqual(
                0,
                len(self.owncloud.validate_struct_txt('mvol-0001-0002-0003', f))
            )

    def test_struct_bad(self):
        """catches illformed struct"""
        with io.StringIO('object\tpage\tmilestone\n'
                         '00000001\t1\n'
                         '00000002\t2\n'
                         'abc\tabc\n'
                         '00000004\t4') as f:
            self.assertTrue(
                len(self.owncloud.validate_struct_txt('mvol-0001-0002-0003', f)) > 0
            )

    def test_struct_correct(self):
        """confirms struct is wellformed, without the extra empty line"""
        with io.StringIO('object\tpage\tmilestone\n'
                         '00000002\t2\n'
                         '00000003\t3\n'
                         '00000004\t4') as f:
            self.assertEqual(
                0,
                len(self.owncloud.validate_struct_txt('mvol-0001-0002-0003', f))
            )

    def test_struct_correct_extra_line(self):
        """confirms struct is wellformed, including ones with an extra empty line at end"""
        with io.StringIO('object\tpage\tmilestone\n'
                         '00000001\t1\n'
                         '00000002\t2\n'
                         '00000003\t3\n'
                         '00000004\t4') as f:
            self.assertEqual(
                0,
                len(self.owncloud.validate_struct_txt('mvol-0001-0002-0003', f))
            )

    def test_pdf_notempty(self):
        """confirms pdf is nonempty, though not whether it's actually a pdf"""
        file = Path('testdocs/mini-sueto.pdf')
        with open(file, 'r') as f:
            self.assertEqual(
                0,
                len(OwnCloudSSH._validate_file_notempty(f))
            )

    def test_pdf_empty(self):
        """catches if pdf is empty file"""
        with io.StringIO('') as f:
            self.assertTrue(len(OwnCloudSSH._validate_file_notempty(f)) > 0)

    def test_mets_xml_pass(self):
        """mets validator confirms wellformed xml following mets standards"""
        file = Path('testdocs/good.mets.xml')
        with open(file, 'r') as f:
            self.assertEqual(
                0,
                len(self.owncloud.validate_mets_xml('mvol-0001-0002-0003', f))
            )

    def test_mets_xml_valid(self):
        """mets validator catches validation errors."""
        with io.StringIO('<mets:mets xmlns:mets="http://www.loc.gov/METS/"/>') as f:
            self.assertTrue(len(self.owncloud.validate_mets_xml('mvol-0001-0002-0003', f)) > 0)

    def test_mets_xml_wellformedness(self):
        """mets validator catches well-formedness errors."""
        with io.StringIO('<not_well></formed_xml>') as f:
            self.assertTrue(len(self.owncloud.validate_mets_xml('mvol-0001-0002-0003', f)) > 0)

    def test_mets_xml_wellformed_not_mets(self):
        """mets validator catches if wellformed, but not at mets standards"""
        with io.StringIO('<notmets/>') as f:
            self.assertTrue(len(self.owncloud.validate_mets_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml_wellformedness(self):
        """dc.xml validator catches well-formedness errors."""
        with io.StringIO('<not_well></formed_xml>') as f:
            self.assertTrue(len(self.owncloud.validate_dc_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml_outer_element(self):
        """dc.xml validator makes sure outer element is <metadata>."""
        f = io.StringIO('<dublin_core><title>test</title><date>2000-01-01</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></dublin_core>')
        self.assertTrue(len(self.owncloud.validate_dc_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml_date(self):
        """dc.xml validator makes sure the text of the date element is yyyy-mm-dd."""
        with io.StringIO('<metadata><title>test</title><date>2000-31-01</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></metadata>') as f:
            self.assertTrue(len(self.owncloud.validate_dc_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml(self):
        """dc.xml validator accepts a correctly formed file."""
        with io.StringIO('<metadata><title>test</title><date>2000-01-31</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></metadata>') as f:
            self.assertEqual(
                0,
                len(self.owncloud.validate_dc_xml('mvol-0001-0002-0003', f))
            )


class TestApfValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owncloud = OwnCloudSSH()

    def test_recursive_ls(self):
        """mock a dummy system to test this."""
        '''
        file = path(<identifier-chunk-in-apf>)
        self.assertItemsEqual(file,<apf-directory>) // self.assertCountEqual("")
        '''
        raise NotImplementedError

    def test_validate(self):
        """mock a dummy system to test this."""
        raise NotImplementedError

if __name__ == '__main__':
    unittest.main()
