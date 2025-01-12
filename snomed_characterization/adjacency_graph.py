from collections import defaultdict
from typing import List, Tuple

from .abstract_graph import AbstractGraph, T


class AdjacencyListGraph(AbstractGraph[T]):
    """
    Represents a graph using an adjacency list.
    """

    def __init__(self):
        self.graph = defaultdict(list)

    def add_node(self, node_id: T):
        """
        Adds a node to the graph.
        """
        if node_id not in self.graph:
            self.graph[node_id] = []

    def add_edge(self, source_node_id: T, target_node_id: T, weight: float = 1.0):
        """
        Adds an edge between two nodes with an optional weight.
        """
        self.graph[source_node_id].append((target_node_id, weight))

    def get_weighted_neighbors(self, node_id: T) -> List[Tuple[T, float]]:
        """
        Returns a list of neighbor nodes and their edge weights for the given node.
        """
        return self.graph[node_id]

    def get_neighbors(self, node_id: T) -> List[T]:
        """
        Returns a list of neighbor nodes and their edge weights for the given node.
        """
        return self.graph[node_id]
