from typing import List
import networkx as nx

# from .adjacency_graph import AdjacencyListGraph
from snomed_characterization.graphs.adjacency_graph import AdjacencyListGraph

from snomed_characterization.snomed_concept import RawSNOMEDConcept


class SNOMEDCompleteGraphBuilder(AdjacencyListGraph[RawSNOMEDConcept]):
    def __init__(self):
        self.graph = nx.DiGraph()
        pass

    def add_edge(
        self,
        source_node_id: RawSNOMEDConcept,
        target_node_id: RawSNOMEDConcept,
        weight: float = 1.0,
        relationship: str = "is_a",
    ):
        self.graph.add_edge(
            source_node_id.concept_id,
            target_node_id.concept_id,
            weight=weight,
            relationship=relationship,
        )

    def add_concept(
        self,
        concept: RawSNOMEDConcept,
        parent_ids: List[RawSNOMEDConcept],
    ):
        """
        Adds a concept to the graph with edges to its parents.
        """
        self.graph.add_node(concept.concept_id, data=concept)
        for parent_id in parent_ids:
            if not self.exists_node(parent_id):
                self.add_concept(concept=parent_id, parent_ids=[])

            if not self.exists_edge(concept, parent_id):
                self.add_edge(concept, parent_id, relationship="is_descendant_of")
                self.add_edge(parent_id, concept, relationship="is_ancestor_of")

    def exists_edge(
        self, source_node_id: RawSNOMEDConcept, target_node_id: RawSNOMEDConcept
    ) -> bool:
        return self.graph.has_edge(source_node_id.concept_id, target_node_id.concept_id)

    def exists_node(self, source_node_id: RawSNOMEDConcept) -> bool:
        """
        Returns True if a path exists between two nodes in the graph.
        """
        return self.graph.has_node(source_node_id.concept_id)
