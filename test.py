import io
import unittest
import os
from digital_collection_validators.classes import *
from pathlib import Path
import re


class TestValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owncloud = DigitalCollectionValidator()
        self.owncloud.connect('s3.lib.uchicago.edu', {})

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


    def test_list_directory(self):
        '''Confirms that all file(s) are listed in chopin, ewm, gms, and speculum directories'''
        # === CHOPIN === #
        chopin1 = self.owncloud.list_directory('chopin-001')
        chopin2 = self.owncloud.list_directory('chopin-017')

        self.assertTrue(set(chopin1) == set(self.owncloud.cs_listdir(self.owncloud.get_path('chopin-001') + '/tifs')))
        self.assertTrue(set(chopin2) == set(self.owncloud.cs_listdir(self.owncloud.get_path('chopin-017') + '/tifs')))

        # === EWM === #
        ewm1 = self.owncloud.list_directory('ewm-0001-0001cr')
        ewm2 = self.owncloud.list_directory('ewm-0009-0004')

        self.assertTrue(ewm1[0] == 'ewm-0001-0001cr.tif')
        self.assertTrue(ewm2[0] == 'ewm-0009-0004.tif')

        # === GMS === #
        gms1 = self.owncloud.list_directory('gms-0019')
        gms2 = self.owncloud.list_directory('gms-0128-005')

        self.assertTrue(set(gms1) == set(self.owncloud.cs_listdir(self.owncloud.get_path('gms-0019') + '/tifs')))
        self.assertTrue(gms2[0] == 'gms-0128-005.tif')

        # === SPECULUM === #
        spec1 = self.owncloud.list_directory('speculum-0003')
        spec2 = self.owncloud.list_directory('speculum-0009-001')

        self.assertTrue(set(spec1) == set(self.owncloud.cs_listdir(self.owncloud.get_path('speculum-0003') + '/tifs')))
        self.assertTrue(spec2[0] == 'speculum-0009-001.tif')


    def test_validate(self):
        '''validates existing tiff files'''

        # === CHOPIN === #
        self.assertFalse(self.owncloud.validate_files('chopin-001-032'))
        self.assertFalse(self.owncloud.validate_files('chopin-010-006'))

        self.assertTrue('tiff missing' in self.owncloud.validate_files('chopin-001-033')[0])
        self.assertTrue('tiff missing' in self.owncloud.validate_files('chopin-010-007')[0])

        # === EWM === #
        self.assertFalse(self.owncloud.validate_files('ewm-0001-0001cr'))
        self.assertFalse(self.owncloud.validate_files('ewm-0009-0004'))

        self.assertTrue('tiff missing' in self.owncloud.validate_files('ewm-0006-0335')[0])
        self.assertTrue('tiff missing' in self.owncloud.validate_files('ewm-0009-0090')[0])

        # === GMS === #
        self.assertFalse(self.owncloud.validate_files('gms-0019-244'))
        self.assertFalse(self.owncloud.validate_files('gms-0062-117'))

        self.assertTrue('tiff missing' in self.owncloud.validate_files('gms-0062-300')[0])
        self.assertTrue('tiff missing' in self.owncloud.validate_files('gms-0019-999')[0])

        # === SPECULUM === #
        self.assertFalse(self.owncloud.validate_files('speculum-0001-001'))
        self.assertFalse(self.owncloud.validate_files('speculum-0017-001'))

        self.assertTrue('tiff missing' in self.owncloud.validate_files('speculum-0001-002')[0])
        self.assertTrue('tiff missing' in self.owncloud.validate_files('speculum-0017-002')[0])

    def test_validate_directories(self):
        '''validates batch of tiff files in directory'''

        self.assertFalse(self.owncloud.validate_tiff_directory('chopin-001','TIFF'))



class TestRacValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rac = RacValidator()
        self.rac.connect('s3.lib.uchicago.edu', {})

    def test_list_directory(self):
        '''Confirms that all tif file(s) are listed in rac directories'''
        rac1 = self.rac.list_dir('rac-0392')
        rac2 = self.rac.list_dir('chess-0392-007')
        rac3 = self.rac.list_dir('rac-1380')
        rac4 = self.rac.list_dir('rose-1380-002')

        self.assertTrue(set(rac1) == set(self.rac.cs_listdir(self.rac.get_path('rac-0392') + '/tifs')))
        self.assertTrue(rac2[0] == 'chess-0392-007.tif')
        self.assertTrue(set(rac3) == set(self.rac.cs_listdir(self.rac.get_path('rac-1380') + '/tifs')))
        self.assertTrue(rac4[0] == 'rose-1380-002.tif')      

    def test_validate(self):
        '''validates existing tiff files'''

        self.assertFalse(self.rac.validate_tiff_files('chess-0392-001'))
        self.assertFalse(self.rac.validate_tiff_files('rose-1380-009'))
        self.assertFalse(self.rac.validate_tiff_files('rose-1380-113'))

        self.assertTrue('tiff missing' in self.rac.validate_tiff_files('chess-0392-999')[0])
        self.assertTrue('tiff missing' in self.rac.validate_tiff_files('rose-1380-999')[0])
        self.assertTrue('tiff missing' in self.rac.validate_tiff_files('rose-1380-592')[0])  



class TestMvolValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mvolowncloud = MvolValidator()
        self.mvolowncloud.connect('s3.lib.uchicago.edu', {})

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
                len(MvolValidator._validate_file_notempty(f))
            )

    def test_pdf_empty(self):
        """catches if pdf is empty file"""
        with io.StringIO('') as f:
            self.assertTrue(len(MvolValidator._validate_file_notempty(f)) > 0)

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
        self.owncloud = ApfValidator()
        self.owncloud.connect('s3.lib.uchicago.edu', {})

    def test_list_dir(self):
        ''' confirms that all tiff files are listed in apf directory'''

        if (self.owncloud.connected):
            path = "/data/voldemort/digital_collections/data/ldr_oc_admin/files/IIIF_Files/"
        else:
            path = "C:/Users/ksong814/Desktop/IIIF_Files/"

        test1 = path + 'apf/1'
        list1 = self.owncloud.cs_listdir(test1)

        fin = []
        for identifier in list1:
            if identifier.endswith('.tif'):
                fin.append(identifier)

        list2 = self.owncloud.list_dir('apf1')

        self.assertTrue(set(fin)==set(list2))
    
    def test_validate(self):
        ''' validates existing tiff files'''

        self.assertFalse(self.owncloud.validate_tiff_files('apf1-00001'))
        self.assertFalse(self.owncloud.validate_tiff_files('apf5-00421'))
        self.assertFalse(self.owncloud.validate_tiff_files('apf8-01199'))
        
        self.assertTrue('tiff missing' in self.owncloud.validate_tiff_files('apf1-98913')[0])
        self.assertTrue('tiff missing' in self.owncloud.validate_tiff_files('apf5-77000')[0])
        self.assertTrue('tiff missing' in self.owncloud.validate_tiff_files('apf8-32145')[0])
        
    
if __name__ == '__main__':
    unittest.main()
