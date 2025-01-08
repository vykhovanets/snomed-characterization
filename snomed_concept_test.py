import unittest

from snomed_concept import SNOMEDConcept


class TestSNOMEDConcept(unittest.TestCase):
    def test_snome_concept_create(self):
        concept = SNOMEDConcept("123456", ["123457", "123458"], ["123459", "123460"])
        self.assertEqual(concept.id, "123456")
        self.assertEqual(concept.parents, ["123457", "123458"])
        self.assertEqual(concept.children, ["123459", "123460"])

    def test_snome_concept_create_no_parents(self):
        concept = SNOMEDConcept("123456", None, ["123459", "123460"])
        self.assertEqual(concept.id, "123456")
        self.assertEqual(concept.parents, None)
        self.assertEqual(concept.children, ["123459", "123460"])

    def test_snome_concept_create_no_children(self):
        concept = SNOMEDConcept("123456", ["123457", "123458"], None)
        self.assertEqual(concept.id, "123456")
        self.assertEqual(concept.parents, ["123457", "123458"])
        self.assertEqual(concept.children, None)
