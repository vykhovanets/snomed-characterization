from abc import ABC, abstractmethod
from typing import List, Tuple, TypeVar, Generic

T = TypeVar("T")


class AbstractGraph(ABC, Generic[T]):
    """
    Abstract base class for representing graphs.
    """

    @abstractmethod
    def add_node(self, node_id: T):
        """
        Adds a node to the graph.
        """
        pass

    @abstractmethod
    def add_edge(self, source_node_id: T, target_node_id: T, weight: float = 1.0):
        """
        Adds an edge between two nodes.
        """
        pass

    @abstractmethod
    def get_neighbors(self, node_id: T) -> List[T]:
        """
        Returns a list of neighbor nodes for the given node.
        """
        pass

    @abstractmethod
    def get_weighted_neighbors(self, node_id: T) -> List[Tuple[T, float]]:
        """
        Returns a list of neighbor nodes and their edge weights for the given node.
        """
        pass
