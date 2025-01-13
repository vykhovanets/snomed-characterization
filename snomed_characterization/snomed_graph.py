from typing import List
import networkx as nx

from .adjacency_graph import AdjacencyListGraph


class SNOMEDGraph(AdjacencyListGraph[int]):
    def __init__(self):
        self.graph = nx.DiGraph()
        pass

    def add_edge(
        self,
        source_node_id: int,
        target_node_id: int,
        weight: float = 1.0,
        relationship: str = "is_a",
    ):
        self.graph.add_edge(
            source_node_id, target_node_id, weight=weight, relationship=relationship
        )

    def add_concept(self, concept_id: int, parent_ids: List[int]):
        """
        Adds a concept to the graph with edges to its parents.
        """
        self.graph.add_node(concept_id)
        for parent_id in parent_ids:
            if not self.exists_node(parent_id):
                self.add_concept(parent_id, [])

            if not self.exists_edge(concept_id, parent_id):
                self.add_edge(concept_id, parent_id, relationship="is_descendant_of")
                self.add_edge(parent_id, concept_id, relationship="is_ancestor_of")

    def exists_edge(self, source_node_id: int, target_node_id: int) -> bool:
        return self.graph.has_edge(source_node_id, target_node_id)

    def exists_node(self, source_node_id: int) -> bool:
        """
        Returns True if a path exists between two nodes in the graph.
        """
        return self.graph.has_node(source_node_id)
