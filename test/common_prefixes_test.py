import unittest
from cogs.extract_task_functions import *


class CommonPrefixesTest(unittest.TestCase):
    def test_dfs(self):
        filters = ['df!help', 'df!generate']
        common_prefixes = find_common_prefixes(filters)
        expected_result = ['df!']
        self.assertEquals(common_prefixes, expected_result)


if __name__ == '__main__':
    unittest.main()
