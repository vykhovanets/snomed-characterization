import unittest

from snomed_characterization.snomed_concept import SNOMEDConcept


class TestSNOMEDConcept(unittest.TestCase):
    def test_snome_concept_create(self):
        concept = SNOMEDConcept(id=1, name="demo")
        self.assertEqual(concept.id, 1)
