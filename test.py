"""test module
"""
from __future__ import absolute_import

import unittest

from src.backend import db_wrapper
class TestStringMethods(unittest.TestCase):
    """unit test class
    """

    def test_connect_database_success(self):
        """test connection function
        """
        flag = True
        try:
            db_wrapper.connect_to_database()
        except:
            flag = False
        self.assertEqual(True, flag)

if __name__ == '__main__':
    unittest.main()
