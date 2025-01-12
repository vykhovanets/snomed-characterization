import unittest
from snomed_characterization.snomed_graph import SNOMEDGraph
import networkx


class SNOMEDGraphTest(unittest.TestCase):
    def setUp(self):
        self.snomed_graph = SNOMEDGraph()

    def test_snome_graph_create(self):
        snomed = SNOMEDGraph()
        # check instance of networkx.Graph
        self.assertIsInstance(snomed.graph, networkx.Graph)

    def test_snome_graph_add_concept(self):
        snomed = SNOMEDGraph()
        snomed.add_concept(1, [2, 3])
        self.assertEqual(list(snomed.graph.nodes), [1, 2, 3])

        # validate edges
        self.assertEqual(list(snomed.graph.edges), [(1, 2), (1, 3)])
