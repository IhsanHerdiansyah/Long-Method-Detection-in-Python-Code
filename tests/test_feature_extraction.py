import unittest

from src.feature_extraction import CodeFormatError, extract_functions


class FeatureExtractionTest(unittest.TestCase):
    def test_extracts_methods_parameters_and_branches(self):
        source = """
class Service:
    def process(self, first, second=1, *args, **kwargs):
        if first:
            for item in args:
                print(item)
        return second
"""
        functions = extract_functions(source)
        self.assertEqual(len(functions), 1)
        function = functions[0]
        self.assertEqual(function.name, "Service.process")
        self.assertEqual(function.parameter_count, 5)
        self.assertEqual(function.branch_count, 2)
        self.assertGreaterEqual(function.nloc, 5)

    def test_plain_snippet_is_wrapped_as_function(self):
        functions = extract_functions("if True:\n    print('ok')")
        self.assertEqual(functions[0].name, "__input_snippet__")
        self.assertEqual(functions[0].branch_count, 1)

    def test_syntax_error_is_reported(self):
        with self.assertRaises(CodeFormatError):
            extract_functions("def broken(:\n    pass")


if __name__ == "__main__":
    unittest.main()

