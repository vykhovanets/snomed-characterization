import unittest
from snomed_characterization.graphs.snomed_graph_builder import SNOMEDGraphBuilder
import networkx


class SNOMEDGraphTest(unittest.TestCase):
    def setUp(self):
        self.snomed_graph = SNOMEDGraphBuilder()

    def test_snomed_graph_create(self):
        snomed = SNOMEDGraphBuilder()
        # check instance of networkx.Graph
        self.assertIsInstance(snomed.graph, networkx.DiGraph)

    def test_snome_graph_add_concept(self):
        snomed = SNOMEDGraphBuilder()
        snomed.add_concept(1, [2, 3])
        self.assertEqual(list(snomed.graph.nodes), [1, 2, 3])

        # validate edges
        self.assertEqual(list(snomed.graph.edges), [(1, 2), (1, 3), (2, 1), (3, 1)])
