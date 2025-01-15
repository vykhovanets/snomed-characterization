from typing import List, Optional
import networkx as nx

from .adjacency_graph import AdjacencyListGraph
from .abstract_graph import T


class SNOMEDGraphBuilder(AdjacencyListGraph[T]):
    def __init__(self):
        self.graph = nx.DiGraph()
        pass

    def add_edge(self, source_node_id: T, target_node_id: T, weight: float = 1.0):
        self.graph.add_edge(source_node_id, target_node_id, weight=weight)

    def add_edge_with_relationship(
        self,
        source_node_id: T,
        target_node_id: T,
        weight: float = 1.0,
        relationship: Optional[str] = None,
    ):
        self.graph.add_edge(
            source_node_id, target_node_id, weight=weight, relationship=relationship
        )

    def add_concept(self, concept_id: T, parent_ids: List[T]):
        """
        Adds a concept to the graph with edges to its parents.
        """
        self.graph.add_node(concept_id)
        for parent_id in parent_ids:
            if not self.exists_node(parent_id):
                self.add_concept(parent_id, [])

            if not self.exists_edge(concept_id, parent_id):
                self.add_edge_with_relationship(
                    concept_id, parent_id, relationship="is_descendant_of"
                )
                self.add_edge_with_relationship(
                    parent_id, concept_id, relationship="is_ancestor_of"
                )

    def exists_edge(self, source_node_id: T, target_node_id: T) -> bool:
        return self.graph.has_edge(source_node_id, target_node_id)

    def exists_node(self, source_node_id: T) -> bool:
        """
        Returns True if a path exists between two nodes in the graph.
        """
        return self.graph.has_node(source_node_id)
