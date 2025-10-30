#!/usr/bin/env python3
"""
Test suite for KSP Contract Translator
"""

import unittest
import os
import sys
import tempfile

# Add parent directory to path to import the translator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from translate_contracts import translate_cfg_file, extract_field_value, simple_translate


class TestFieldExtraction(unittest.TestCase):
    """Test field extraction from .cfg lines"""
    
    def test_extract_simple_title(self):
        line = "\ttitle = Orbit the first artificial satellite."
        prefix, value = extract_field_value(line, 'title')
        self.assertEqual(prefix, "\ttitle = ")
        self.assertEqual(value, "Orbit the first artificial satellite.")
    
    def test_extract_with_extra_spaces(self):
        line = "  description  =  We want you to place a satellite in orbit."
        prefix, value = extract_field_value(line, 'description')
        self.assertEqual(prefix, "  description  =  ")
        self.assertEqual(value, "We want you to place a satellite in orbit.")
    
    def test_extract_notes(self):
        line = "\tnotes = Complete the following:"
        prefix, value = extract_field_value(line, 'notes')
        self.assertEqual(prefix, "\tnotes = ")
        self.assertEqual(value, "Complete the following:")
    
    def test_extract_agent(self):
        line = "\tagent = Space Penguins, Inc"
        prefix, value = extract_field_value(line, 'agent')
        self.assertEqual(prefix, "\tagent = ")
        self.assertEqual(value, "Space Penguins, Inc")
    
    def test_no_match(self):
        line = "\tname = First Orbit"
        prefix, value = extract_field_value(line, 'title')
        self.assertIsNone(prefix)
        self.assertIsNone(value)


class TestSimpleTranslation(unittest.TestCase):
    """Test the simple translation function"""
    
    def test_exact_match(self):
        text = "Complete the following:"
        result = simple_translate(text)
        self.assertEqual(result, "Complete o seguinte:")
    
    def test_partial_match(self):
        text = "Crash a probe on the Moon"
        result = simple_translate(text)
        # Should contain translated parts
        self.assertIn("Colida uma sonda em", result)
    
    def test_empty_string(self):
        self.assertEqual(simple_translate(""), "")
    
    def test_whitespace_only(self):
        self.assertEqual(simple_translate("   "), "   ")


class TestCfgTranslation(unittest.TestCase):
    """Test full .cfg file translation"""
    
    def test_translate_simple_contract(self):
        """Test translating a simple contract structure"""
        input_cfg = """CONTRACT_TYPE
{
\tname = First Orbit
\tgroup = STGUnmannedMissions
\ttitle = Let's get a probe into orbit

\tnotes = Complete the following:
\tsynopsis = Send a probe to space and get it into orbit around our homeworld
\tcompletedMessage = You did it! You've successfully gotten a probe into orbit
\tagent = Space Penguins, Inc
\tcancellable = true
}
"""
        result = translate_cfg_file(input_cfg)
        
        # Check that structure is preserved
        self.assertIn("CONTRACT_TYPE", result)
        self.assertIn("\tname = First Orbit", result)
        self.assertIn("\tgroup = STGUnmannedMissions", result)
        self.assertIn("\tcancellable = true", result)
        
        # Check that translations are applied
        self.assertIn("Vamos colocar uma sonda em órbita", result)
        self.assertIn("Complete o seguinte:", result)
        # Agent name should not be translated (it's a company name)
        self.assertIn("Space Penguins, Inc", result)
    
    def test_preserve_non_translatable_fields(self):
        """Test that non-translatable fields are preserved"""
        input_cfg = """CONTRACT_TYPE
{
\tname = Test Contract
\ttargetBody = HomeWorld()
\tmaxCompletions = 1
\trewardScience = 5.0
\ttitle = Orbit a probe and return it safely home
}
"""
        result = translate_cfg_file(input_cfg)
        
        # Check non-translatable fields are unchanged
        self.assertIn("\tname = Test Contract", result)
        self.assertIn("\ttargetBody = HomeWorld()", result)
        self.assertIn("\tmaxCompletions = 1", result)
        self.assertIn("\trewardScience = 5.0", result)
        
        # Check title is translated
        self.assertIn("Coloque uma sonda em órbita e retorne-a para casa em segurança", result)
    
    def test_preserve_indentation(self):
        """Test that indentation is preserved"""
        input_cfg = """\tPARAMETER
\t{
\t\tname = Orbit
\t\ttype = Orbit
\t\ttitle = Let's get a probe into orbit
\t}
"""
        result = translate_cfg_file(input_cfg)
        
        # Check indentation is preserved
        lines = result.split('\n')
        self.assertTrue(lines[0].startswith('\tPARAMETER'))
        self.assertTrue(lines[1].startswith('\t{'))
        self.assertTrue(lines[2].startswith('\t\tname = Orbit'))
        self.assertTrue(lines[3].startswith('\t\ttype = Orbit'))
        self.assertTrue(lines[4].startswith('\t\ttitle = '))
    
    def test_preserve_comments(self):
        """Test that comments are preserved"""
        input_cfg = """// This is a comment
CONTRACT_TYPE
{
\t// Another comment
\ttitle = Let's get a probe into orbit
\t// name = old value
}
"""
        result = translate_cfg_file(input_cfg)
        
        # Comments should be preserved
        self.assertIn("// This is a comment", result)
        self.assertIn("\t// Another comment", result)
        self.assertIn("\t// name = old value", result)


class TestEndToEnd(unittest.TestCase):
    """End-to-end tests"""
    
    def test_full_contract_structure(self):
        """Test a complete contract with nested structures"""
        input_cfg = """CONTRACT_TYPE
{
\tname = First Orbit
\tgroup = STGUnmannedMissions
\ttitle = Let's get a probe into orbit

\ttopic = orbit
\tsubject = HomeWorld()
\tmotivation = Because....

\tnotes = Complete the following:
\tsynopsis = Send a probe to space and get it into orbit around our homeworld
\tcompletedMessage = You did it! You've successfully gotten a probe into orbit
\tagent = Space Penguins, Inc
\tcancellable = true
\tdeclinable = true
\tprestige = Exceptional
\ttargetBody = HomeWorld()
\tmaxCompletions = 1
\trewardScience = 5.0
\t
\tPARAMETER
\t{
\t\tname = Orbit
\t\ttype = Orbit
\t\tsituation = ORBITING
\t\tminInclination = 0
\t}
}
"""
        result = translate_cfg_file(input_cfg)
        
        # Check structure preservation
        self.assertIn("CONTRACT_TYPE", result)
        self.assertIn("\tPARAMETER", result)
        self.assertIn("\t{", result)
        self.assertIn("\t}", result)
        
        # Check code fields are unchanged
        self.assertIn("\tname = First Orbit", result)
        self.assertIn("\tgroup = STGUnmannedMissions", result)
        self.assertIn("\ttopic = orbit", result)
        self.assertIn("\tsubject = HomeWorld()", result)
        self.assertIn("\ttargetBody = HomeWorld()", result)
        self.assertIn("\tmaxCompletions = 1", result)
        self.assertIn("\trewardScience = 5.0", result)
        self.assertIn("\t\tname = Orbit", result)
        self.assertIn("\t\ttype = Orbit", result)
        self.assertIn("\t\tsituation = ORBITING", result)
        self.assertIn("\t\tminInclination = 0", result)
        
        # Check translations
        self.assertIn("Vamos colocar uma sonda em órbita", result)
        # motivation field should NOT be translated (not in the translatable fields list)
        self.assertIn("\tmotivation = Because....", result)
        self.assertIn("Complete o seguinte:", result)
        self.assertIn("Você conseguiu", result)
        self.assertIn("Space Penguins, Inc", result)  # Company name preserved


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFieldExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestSimpleTranslation))
    suite.addTests(loader.loadTestsFromTestCase(TestCfgTranslation))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
