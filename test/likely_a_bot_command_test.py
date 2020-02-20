import unittest
from cogs.extract_task_functions import *


class BotCommandTest(unittest.TestCase):
    def test_harmless_sentence(self):
        s = 'One plus one equals two'
        is_bot_command = likely_a_bot_command(s)
        self.assertFalse(is_bot_command)

    def test_df_generate(self):
        s = 'df!generate Rusty'
        expected_result = 'df!generate'
        is_bot_command = likely_a_bot_command(s)
        self.assertEqual(is_bot_command, 'df!generate')

    def test_mention(self):
        s = '@Rusty#0000'
        is_bot_command = likely_a_bot_command(s)
        self.assertFalse(is_bot_command)

    def test_empty_message(self):
        s = ''
        is_bot_command = likely_a_bot_command(s)
        self.assertFalse(is_bot_command)

    def test_one_word_sentence(self):
        s = 'Hello!'
        is_bot_command = likely_a_bot_command(s)
        self.assertFalse(is_bot_command)

    def test_help(self):
        s = '=help'
        is_bot_command = likely_a_bot_command(s)
        expected_result = '=help'
        self.assertEqual(is_bot_command, expected_result)

    def test_really_excited(self):
        s = 'Hello!!!!'
        is_bot_command = likely_a_bot_command(s)
        self.assertFalse(is_bot_command)

    def test_contraction(self):
        s = 'I\'m the best'
        is_bot_command = likely_a_bot_command(s)
        self.assertFalse(is_bot_command)


if __name__ == '__main__':
    unittest.main()
