import io
import unittest
from digital_collection_validators.classes import *
from pathlib import Path


class TestSSH(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owncloud = OwnCloudSSH()

    def test_is_identifier(self):
        """ 
        Be sure that identifiers conform to their filenaming spec. Note
        that this function does not need to confirm that an identifier with
        that name currently exists- it only needs to confirm that an identifier
            with that name would be legal.
        """
        self.assertEqual(False,self.owncloud.is_identifier('apf'))
        self.assertEqual(False,self.owncloud.is_identifier('apf1'))
        self.assertEqual(False,self.owncloud.is_identifier('apfx'))
        self.assertEqual(False,self.owncloud.is_identifier('apf1-0001'))
        self.assertEqual(True,self.owncloud.is_identifier('apf1-00001'))
        self.assertEqual(True,self.owncloud.is_identifier('apf8-00001'))
        
        self.assertEqual(False,self.owncloud.is_identifier('chopin'))
        self.assertEqual(False,self.owncloud.is_identifier('chopin-'))
        self.assertEqual(False,self.owncloud.is_identifier('chopin-abc'))
        self.assertEqual(False,self.owncloud.is_identifier('chopin-0000'))
        self.assertEqual(True,self.owncloud.is_identifier('chopin-001'))
        self.assertEqual(True,self.owncloud.is_identifier('chopin-036'))

        self.assertEqual(False,self.owncloud.is_identifier('ewm'))
        self.assertEqual(False,self.owncloud.is_identifier('ewm-00001'))
        self.assertEqual(False,self.owncloud.is_identifier('ewm-abcd'))
        self.assertEqual(True,self.owncloud.is_identifier('ewm-0001'))

        self.assertEqual(False,self.owncloud.is_identifier('gms'))
        self.assertEqual(False,self.owncloud.is_identifier('gms-'))
        self.assertEqual(False,self.owncloud.is_identifier('gms-00111'))
        self.assertEqual(True,self.owncloud.is_identifier('gms-0001'))

        self.assertEqual(False,self.owncloud.is_identifier('mvol'))
        self.assertEqual(False,self.owncloud.is_identifier('mvol-0000'))
        self.assertEqual(False,self.owncloud.is_identifier('mvol-0000-0001'))
        self.assertEqual(True,self.owncloud.is_identifier('mvol-0001-0002-0003'))
        self.assertEqual(True,self.owncloud.is_identifier('mvol-0002-0004-0000'))

        self.assertEqual(False,self.owncloud.is_identifier('speculum'))
        self.assertEqual(False,self.owncloud.is_identifier('speculum-01000'))
        self.assertEqual(False,self.owncloud.is_identifier('speculum-abcd'))
        self.assertEqual(True,self.owncloud.is_identifier('speculum-0001'))

    def test_is_identifier_chunk(self):
        """ 
        Be sure that identifier chunks conform to their filenaming spec. Note
        that this function does not need to confirm that an identifier chunk with
        that name currently exists- it only needs to confirm that one with that
        name would be legal.
        """
        self.assertEqual(True,self.owncloud.is_identifier_chunk('apf'))
        self.assertEqual(True,self.owncloud.is_identifier_chunk('apf1'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('apfx'))
        self.assertEqual(True,self.owncloud.is_identifier_chunk('apf1-00001'))
        
        self.assertEqual(True,self.owncloud.is_identifier_chunk('chopin'))
        self.assertEqual(True,self.owncloud.is_identifier_chunk('chopin-001'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('chopin1'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('chopin-abc'))

        self.assertEqual(True,self.owncloud.is_identifier_chunk('ewm'))
        self.assertEqual(True,self.owncloud.is_identifier_chunk('ewm-0001'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('ewm-abcd'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('ewm-'))

        self.assertEqual(True,self.owncloud.is_identifier_chunk('gms'))
        self.assertEqual(True,self.owncloud.is_identifier_chunk('gms-0001'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('gms-'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('gms-abcd'))

        self.assertEqual(True,self.owncloud.is_identifier_chunk('mvol'))
        self.assertEqual(True,self.owncloud.is_identifier_chunk('mvol-0001'))
        self.assertEqual(True,self.owncloud.is_identifier_chunk('mvol-0001-0002-0003'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('mvol-'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('mvol-001-0002'))

        self.assertEqual(True,self.owncloud.is_identifier_chunk('speculum'))
        self.assertEqual(True,self.owncloud.is_identifier_chunk('speculum-0001'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('speculum-'))
        self.assertEqual(False,self.owncloud.is_identifier_chunk('speculum-00001'))
        

class TestMvolValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mvolowncloud = MvolOwnCloudSSH()

    def test_struct_txt_has_headers(self):
        """struct.txt validator requires headers."""
        with io.StringIO('00000001\t1\n'
                            '00000002\t2\n'
                            '00000003\t3\n'
                            '00000004\t4') as f:
            self.assertTrue(
                len(self.mvolowncloud.validate_struct_txt('mvol-0001-0002-0003', f)) > 0
            )

    def test_struct_txt_has_commas(self):
        """struct.txt validator requires headers."""
        with io.StringIO('object,page,milestone\n'
                            '00000002,2,\n'
                            '00000003,3,\n'
                            '00000004,4,') as f:
            self.assertTrue(
                len(self.mvolowncloud.validate_struct_txt('mvol-0001-0002-0003', f)) > 0
            )

    def test_struct_txt_has_tabs(self):
        """struct.txt validator requires headers."""
        with io.StringIO('object\tpage\tmilestone\n'
                            '00000002\t2\n'
                            '00000003\t3\n'
                            '00000004\t4') as f:
            self.assertEqual(
                0,
                len(self.mvolowncloud.validate_struct_txt('mvol-0001-0002-0003', f))
            )

    def test_struct_bad(self):
        """catches illformed struct"""
        with io.StringIO('object\tpage\tmilestone\n'
                            '00000001\t1\n'
                            '00000002\t2\n'
                            'abc\tabc\n'
                            '00000004\t4') as f:
            self.assertTrue(
                len(self.mvolowncloud.validate_struct_txt('mvol-0001-0002-0003', f)) > 0
            )

    def test_struct_correct(self):
        """confirms struct is wellformed, without the extra empty line"""
        with io.StringIO('object\tpage\tmilestone\n'
                            '00000002\t2\n'
                            '00000003\t3\n'
                            '00000004\t4') as f:
            self.assertEqual(
                0,
                len(self.mvolowncloud.validate_struct_txt('mvol-0001-0002-0003', f))
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
                len(self.mvolowncloud.validate_struct_txt('mvol-0001-0002-0003', f))
            )

    def test_pdf_notempty(self):
        """confirms pdf is nonempty, though not whether it's actually a pdf"""
        file = Path('testdocs/mini-sueto.pdf')
        with open(file, 'r') as f:
            self.assertEqual(
                0,
                len(MvolOwnCloudSSH._validate_file_notempty(f))
            )

    def test_pdf_empty(self):
        """catches if pdf is empty file"""
        with io.StringIO('') as f:
            self.assertTrue(len(MvolOwnCloudSSH._validate_file_notempty(f)) > 0)

    def test_mets_xml_pass(self):
        """mets validator confirms wellformed xml following mets standards"""
        file = Path('testdocs/good.mets.xml')
        with open(file, 'r') as f:
            self.assertEqual(
                0,
                len(self.mvolowncloud.validate_mets_xml('mvol-0001-0002-0003', f))
            )

    def test_mets_xml_valid(self):
        """mets validator catches validation errors."""
        with io.StringIO('<mets:mets xmlns:mets="http://www.loc.gov/METS/"/>') as f:
            self.assertTrue(len(self.mvolowncloud.validate_mets_xml('mvol-0001-0002-0003', f)) > 0)

    def test_mets_xml_wellformedness(self):
        """mets validator catches well-formedness errors."""
        with io.StringIO('<not_well></formed_xml>') as f:
            self.assertTrue(len(self.mvolowncloud.validate_mets_xml('mvol-0001-0002-0003', f)) > 0)

    def test_mets_xml_wellformed_not_mets(self):
        """mets validator catches if wellformed, but not at mets standards"""
        with io.StringIO('<notmets/>') as f:
            self.assertTrue(len(self.mvolowncloud.validate_mets_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml_wellformedness(self):
        """dc.xml validator catches well-formedness errors."""
        with io.StringIO('<not_well></formed_xml>') as f:
            self.assertTrue(len(self.mvolowncloud.validate_dc_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml_outer_element(self):
        """dc.xml validator makes sure outer element is <metadata>."""
        f = io.StringIO('<dublin_core><title>test</title><date>2000-01-01</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></dublin_core>')
        self.assertTrue(len(self.mvolowncloud.validate_dc_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml_date(self):
        """dc.xml validator makes sure the text of the date element is yyyy-mm-dd."""
        with io.StringIO('<metadata><title>test</title><date>2000-31-01</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></metadata>') as f:
            self.assertTrue(len(self.mvolowncloud.validate_dc_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml(self):
        """dc.xml validator accepts a correctly formed file."""
        with io.StringIO('<metadata><title>test</title><date>2000-01-31</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></metadata>') as f:
            self.assertEqual(
                0,
                len(self.mvolowncloud.validate_dc_xml('mvol-0001-0002-0003', f))
            )


class TestApfValidator(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owncloud = ApfOwnCloudSSH()
        self.owncloud.connect('s3.lib.uchicago.edu', {})

    def test_list_dir(self):
        ''' confirms that all json files are listed in apf directory'''

        path = "/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/"

        #ssh = paramiko.SSHClient()
        #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #ssh.connect('s3.lib.uchicago.edu', username='ksong814')
        #ftp = ssh.open_sftp()
        test1 = path + 'apf/1'
        list1 = self.owncloud.ftp.listdir(test1)

        for identifier in list1:
            if identifier.endswith('.json'):
                print(identifier)
                list1.remove(identifier)
        #self.assertCountEqual(list1,self.owncloud.list_dir('apf1'))
        list2 = self.owncloud.list_dir('apf1')
        #print(list1)
        #print(list2)
        #self.assertTrue(set(list1)==set(list2))
        

    #def test_validate(self):
    #    """mock a dummy system to test this."""
    #    raise NotImplementedError
    

if __name__ == '__main__':
    unittest.main()
