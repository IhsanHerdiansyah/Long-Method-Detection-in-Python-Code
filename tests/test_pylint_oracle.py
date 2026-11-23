import unittest

from src.examples import LONG_METHOD, SHORT_METHOD
from src.pylint_oracle import detect_r0915


class PylintOracleTest(unittest.TestCase):
    def test_long_example_triggers_r0915(self):
        messages = detect_r0915(LONG_METHOD)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["message_id"], "R0915")

    def test_short_example_does_not_trigger_r0915(self):
        self.assertEqual(detect_r0915(SHORT_METHOD), [])


if __name__ == "__main__":
    unittest.main()
