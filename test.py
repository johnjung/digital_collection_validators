import io
import unittest
import os
import re
import sqlite3

from digital_collection_validators.classes import *
from pathlib import Path


class TestValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = DigitalCollectionValidator()
        self.validator.connect_to_db('testdocs/validation_test.db')

    def test_get_identifiers_from_db(self):
        self.assertEqual(
            self.validator.get_identifiers_from_db('mvol', True),
            [
                'mvol-0005-0001-0001',
                'mvol-0005-0001-0002',
                'mvol-0005-0001-0003',
                'mvol-0005-0001-0004',
                'mvol-0005-0002-0001',
                'mvol-0005-0002-0002',
                'mvol-0005-0002-0003',
                'mvol-0005-0002-0004',
                'mvol-0005-0003-0001',
                'mvol-0005-0003-0003',
                'mvol-0005-0003-0004',
                'mvol-0005-0003-0005',
                'mvol-0005-0004-0001',
                'mvol-0005-0004-0002',
                'mvol-0005-0004-0003'
            ]
        )

        self.assertEqual(
            self.validator.get_identifiers_from_db('mvol', False),
            [
                'mvol-0005-0001-0001',
                'mvol-0005-0001-0002',
                'mvol-0005-0001-0003',
                'mvol-0005-0001-0004',
                'mvol-0005-0002-0001',
                'mvol-0005-0002-0002',
                'mvol-0005-0002-0003',
                'mvol-0005-0002-0004',
                'mvol-0005-0003-0001',
                'mvol-0005-0003-0002',
                'mvol-0005-0003-0003',
                'mvol-0005-0003-0004',
                'mvol-0005-0003-0005',
                'mvol-0005-0003-0006',
                'mvol-0005-0004-0001',
                'mvol-0005-0004-0002',
                'mvol-0005-0004-0003'
            ]
        )

        self.assertEqual(
            self.validator.get_identifiers_from_db('mvol-0005-0001', True),
            [
                'mvol-0005-0001-0001',
                'mvol-0005-0001-0002',
                'mvol-0005-0001-0003',
                'mvol-0005-0001-0004'
            ]
        )

        self.assertEqual(
            self.validator.get_identifiers_from_db('mvol-0005-0001-0001', True),
            [
                'mvol-0005-0001-0001'
            ]
        )

    def test_get_identifier_chunk_children_from_db(self):
        self.assertEqual(
            self.validator.get_identifier_chunk_children_from_db('mvol'),
            ['mvol-0005']
        )

        self.assertEqual(
            self.validator.get_identifier_chunk_children_from_db('mvol-0005'),
            ['mvol-0005-0001', 'mvol-0005-0002', 'mvol-0005-0003', 'mvol-0005-0004']
        )

        self.assertEqual(
            self.validator.get_identifier_chunk_children_from_db('mvol-0005-0001'),
            ['mvol-0005-0001-0001', 'mvol-0005-0001-0002', 'mvol-0005-0001-0003', 'mvol-0005-0001-0004']
        )

        self.assertEqual(
            self.validator.get_identifier_chunk_children_from_db('mvol-0005-0001-0001'),
            []
        )

    def test_is_identifier(self):
        """ 
        Be sure that identifiers conform to their filenaming spec. Note
        that this function does not need to confirm that an identifier with
        that name currently exists- it only needs to confirm that an identifier
            with that name would be legal.
        """
        self.assertEqual(False,self.validator.is_identifier('apf'))
        self.assertEqual(False,self.validator.is_identifier('apf1'))
        self.assertEqual(False,self.validator.is_identifier('apfx'))
        self.assertEqual(False,self.validator.is_identifier('apf1-0001'))
        self.assertEqual(True,self.validator.is_identifier('apf1-00001'))
        self.assertEqual(True,self.validator.is_identifier('apf8-00001'))
        
        self.assertEqual(False,self.validator.is_identifier('chopin'))
        self.assertEqual(False,self.validator.is_identifier('chopin-'))
        self.assertEqual(False,self.validator.is_identifier('chopin-abc'))
        self.assertEqual(False,self.validator.is_identifier('chopin-0000'))
        self.assertEqual(True,self.validator.is_identifier('chopin-001'))
        self.assertEqual(True,self.validator.is_identifier('chopin-036'))

        self.assertEqual(False,self.validator.is_identifier('ewm'))
        self.assertEqual(False,self.validator.is_identifier('ewm-00001'))
        self.assertEqual(False,self.validator.is_identifier('ewm-abcd'))
        self.assertEqual(True,self.validator.is_identifier('ewm-0001'))

        self.assertEqual(False,self.validator.is_identifier('gms'))
        self.assertEqual(False,self.validator.is_identifier('gms-'))
        self.assertEqual(False,self.validator.is_identifier('gms-00111'))
        self.assertEqual(True,self.validator.is_identifier('gms-0001'))

        self.assertEqual(False,self.validator.is_identifier('mvol'))
        self.assertEqual(False,self.validator.is_identifier('mvol-0000'))
        self.assertEqual(False,self.validator.is_identifier('mvol-0000-0001'))
        self.assertEqual(True,self.validator.is_identifier('mvol-0001-0002-0003'))
        self.assertEqual(True,self.validator.is_identifier('mvol-0002-0004-0000'))

        self.assertEqual(False,self.validator.is_identifier('speculum'))
        self.assertEqual(False,self.validator.is_identifier('speculum-01000'))
        self.assertEqual(False,self.validator.is_identifier('speculum-abcd'))
        self.assertEqual(True,self.validator.is_identifier('speculum-0001'))

    def test_is_identifier_chunk(self):
        """ 
        Be sure that identifier chunks conform to their filenaming spec. Note
        that this function does not need to confirm that an identifier chunk with
        that name currently exists- it only needs to confirm that one with that
        name would be legal.
        """
        self.assertEqual(True,self.validator.is_identifier_chunk('apf'))
        self.assertEqual(True,self.validator.is_identifier_chunk('apf1'))
        self.assertEqual(False,self.validator.is_identifier_chunk('apfx'))
        self.assertEqual(True,self.validator.is_identifier_chunk('apf1-00001'))
        
        self.assertEqual(True,self.validator.is_identifier_chunk('chopin'))
        self.assertEqual(True,self.validator.is_identifier_chunk('chopin-001'))
        self.assertEqual(False,self.validator.is_identifier_chunk('chopin1'))
        self.assertEqual(False,self.validator.is_identifier_chunk('chopin-abc'))

        self.assertEqual(True,self.validator.is_identifier_chunk('ewm'))
        self.assertEqual(True,self.validator.is_identifier_chunk('ewm-0001'))
        self.assertEqual(False,self.validator.is_identifier_chunk('ewm-abcd'))
        self.assertEqual(False,self.validator.is_identifier_chunk('ewm-'))

        self.assertEqual(True,self.validator.is_identifier_chunk('gms'))
        self.assertEqual(True,self.validator.is_identifier_chunk('gms-0001'))
        self.assertEqual(False,self.validator.is_identifier_chunk('gms-'))
        self.assertEqual(False,self.validator.is_identifier_chunk('gms-abcd'))

        self.assertEqual(True,self.validator.is_identifier_chunk('mvol'))
        self.assertEqual(True,self.validator.is_identifier_chunk('mvol-0001'))
        self.assertEqual(True,self.validator.is_identifier_chunk('mvol-0001-0002-0003'))
        self.assertEqual(False,self.validator.is_identifier_chunk('mvol-'))
        self.assertEqual(False,self.validator.is_identifier_chunk('mvol-001-0002'))

        self.assertEqual(True,self.validator.is_identifier_chunk('speculum'))
        self.assertEqual(True,self.validator.is_identifier_chunk('speculum-0001'))
        self.assertEqual(False,self.validator.is_identifier_chunk('speculum-'))
        self.assertEqual(False,self.validator.is_identifier_chunk('speculum-00001'))


class TestMvolValidator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = MvolValidator()

    def test_struct_txt_has_headers(self):
        """struct.txt validator requires headers."""
        with io.StringIO('00000001\t1\n'
                            '00000002\t2\n'
                            '00000003\t3\n'
                            '00000004\t4') as f:
            self.assertTrue(
                len(self.validator.validate_struct_txt('mvol-0001-0002-0003', f)) > 0
            )

    def test_struct_txt_has_commas(self):
        """struct.txt validator requires headers."""
        with io.StringIO('object,page,milestone\n'
                            '00000002,2,\n'
                            '00000003,3,\n'
                            '00000004,4,') as f:
            self.assertTrue(
                len(self.validator.validate_struct_txt('mvol-0001-0002-0003', f)) > 0
            )

    def test_struct_txt_has_tabs(self):
        """struct.txt validator requires headers."""
        with io.StringIO('object\tpage\tmilestone\n'
                            '00000002\t2\n'
                            '00000003\t3\n'
                            '00000004\t4') as f:
            self.assertEqual(
                0,
                len(self.validator.validate_struct_txt('mvol-0001-0002-0003', f))
            )

    def test_struct_bad(self):
        """catches illformed struct"""
        with io.StringIO('object\tpage\tmilestone\n'
                            '00000001\t1\n'
                            '00000002\t2\n'
                            'abc\tabc\n'
                            '00000004\t4') as f:
            self.assertTrue(
                len(self.validator.validate_struct_txt('mvol-0001-0002-0003', f)) > 0
            )

    def test_struct_correct(self):
        """confirms struct is wellformed, without the extra empty line"""
        with io.StringIO('object\tpage\tmilestone\n'
                            '00000002\t2\n'
                            '00000003\t3\n'
                            '00000004\t4') as f:
            self.assertEqual(
                0,
                len(self.validator.validate_struct_txt('mvol-0001-0002-0003', f))
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
                len(self.validator.validate_struct_txt('mvol-0001-0002-0003', f))
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

    def test_dc_xml_wellformedness(self):
        """dc.xml validator catches well-formedness errors."""
        with io.StringIO('<not_well></formed_xml>') as f:
            self.assertTrue(len(self.validator.validate_dc_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml_outer_element(self):
        """dc.xml validator makes sure outer element is <metadata>."""
        f = io.StringIO('<dublin_core><title>test</title><date>2000-01-01</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></dublin_core>')
        self.assertTrue(len(self.validator.validate_dc_xml('mvol-0001-0002-0003', f)) > 0)

    def test_dc_xml(self):
        """dc.xml validator accepts a correctly formed file."""
        with io.StringIO('<metadata><title>test</title><date>2000-01-31</date><description>test</description><identifier>mvol-0004-1900-0101</identifier></metadata>') as f:
            self.assertEqual(
                0,
                len(self.validator.validate_dc_xml('mvol-0001-0002-0003', f))
            )

    
if __name__ == '__main__':
    unittest.main()
