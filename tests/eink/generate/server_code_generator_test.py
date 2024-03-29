import os
import unittest

from eink.generate import ServerCodeGenerator
from eink.project.project import Project


class ServerCodeGeneratorTest(unittest.TestCase):
    """Tests the ``ServerCodeGenerator`` class."""

    def test_validate_server_dir(self):
        """Test ``ServerCodeGenerator._validate_server_dir``."""
        # Test that the following doesn't raise
        root_dir = Project.root_dir()
        ServerCodeGenerator._validate_server_dir(root_dir)
        ServerCodeGenerator._validate_server_dir(
            os.path.join(root_dir, 'does_not_exist'))
        ServerCodeGenerator._validate_server_dir(os.path.join(root_dir, '..'))

        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_server_dir(
                os.path.join(root_dir, 'does_not_exist', 'nested'))

    def test_validate_client_dir(self):
        """Test ``ServerCodeGenerator._validate_client_dir``."""
        # Test that the following doesn't raise
        dir1 = Project.images_dir()
        dir2 = Project.client_code_dir()
        ServerCodeGenerator._validate_client_dir(dir1, dir2)
        ServerCodeGenerator._validate_client_dir(
            dir1, os.path.join(dir2, 'does_not_exist'))
        ServerCodeGenerator._validate_client_dir(
            dir1, os.path.join(dir2, '..'))

        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_client_dir(
                dir1, os.path.join(dir2, 'does_not_exist', 'nested'))
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_client_dir(dir1, dir1)
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_client_dir(
                dir1, os.path.join(dir1, 'subdir', '..'))
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_client_dir(
                os.path.join(dir1, 'subdir', '..'), dir1)

    def test_validate_url(self):
        """Test ``ServerCodeGenerator._validate_url``."""
        # Test that the following doesn't raise
        ServerCodeGenerator._validate_url('http://www.example.com')
        ServerCodeGenerator._validate_url('http://www.example.com/foo')
        ServerCodeGenerator._validate_url(
            'http://www.example.com:1234/foo?bar=baz\u00e9')

        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_url('https://www.example.com/')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_url('ftp://www.example.com/')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_url('')

    def test_validate_non_empty(self):
        """Test ``ServerCodeGenerator._validate_non_empty``."""
        # Test that the following doesn't raise
        ServerCodeGenerator._validate_non_empty('something')
        ServerCodeGenerator._validate_non_empty(' ')
        ServerCodeGenerator._validate_non_empty('\u00e9')

        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_non_empty('')

    def test_is_positive_int(self):
        """Test ``ServerCodeGenerator._is_positive_int``."""
        self.assertTrue(ServerCodeGenerator._is_positive_int('1'))
        self.assertTrue(ServerCodeGenerator._is_positive_int('12345'))
        self.assertTrue(ServerCodeGenerator._is_positive_int('98765'))
        self.assertFalse(ServerCodeGenerator._is_positive_int('-42'))
        self.assertFalse(ServerCodeGenerator._is_positive_int('0'))
        self.assertFalse(ServerCodeGenerator._is_positive_int('01'))
        self.assertFalse(ServerCodeGenerator._is_positive_int('4.5'))
        self.assertFalse(ServerCodeGenerator._is_positive_int('7.0'))
        self.assertFalse(ServerCodeGenerator._is_positive_int('123abc'))
        self.assertFalse(ServerCodeGenerator._is_positive_int('foo'))
        self.assertFalse(ServerCodeGenerator._is_positive_int(''))

    def test_validate_positive_int(self):
        """Test ``ServerCodeGenerator._validate_positive_int``."""
        # Test that the following doesn't raise
        ServerCodeGenerator._validate_positive_int('1')
        ServerCodeGenerator._validate_positive_int('12345')
        ServerCodeGenerator._validate_positive_int('98765')

        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_positive_int('-42')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_positive_int('0')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_positive_int('01')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_positive_int('4.5')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_positive_int('7.0')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_positive_int('123abc')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_positive_int('foo')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_positive_int('')

    def test_validate_1_to_n(self):
        """Test ``ServerCodeGenerator._validate_1_to_n``."""
        # Test that the following doesn't raise
        ServerCodeGenerator._validate_1_to_n(5, '1')
        ServerCodeGenerator._validate_1_to_n(12345, '12345')
        ServerCodeGenerator._validate_1_to_n(1000000, '98765')

        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(5, '6')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(5, '84')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(1, '2')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(12345, '12346')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(100, '-42')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(10, '0')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(4, '01')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(12, '4.5')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(900, '7.0')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(1000000, '123abc')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(1000, 'foo')
        with self.assertRaises(ValueError):
            ServerCodeGenerator._validate_1_to_n(55, '')
