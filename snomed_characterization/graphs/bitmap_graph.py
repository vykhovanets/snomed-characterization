from typing import Dict, List, Optional, Tuple
from pyroaring import BitMap

IS_ANCESTOR_OF = "is_ancestor_of"
IS_DESCENDANT_OF = "is_descendant_of"


class BitMapGraph:
    def __init__(self):
        self.relationships: Dict[Tuple[int, str], BitMap] = {}
        self.nodes = BitMap()

    def add_edge(self, source_node_id: int, target_node_id: int, weight: float = 1.0):
        """Add basic edge between nodes."""
        self.add_edge_with_relationship(source_node_id, target_node_id, weight)

    def add_edge_with_relationship(
        self,
        source_node_id: int,
        target_node_id: int,
        weight: float = 1.0,
        relationship: Optional[str] = None,
    ):
        """Add edge with optional relationship type."""
        # Ensure nodes exist
        self.nodes.add(source_node_id)
        self.nodes.add(target_node_id)

        # Initialize BitMaps if they don't exist
        if (source_node_id, IS_ANCESTOR_OF) not in self.relationships:
            self.relationships[source_node_id, IS_ANCESTOR_OF] = BitMap()
        if (target_node_id, IS_DESCENDANT_OF) not in self.relationships:
            self.relationships[target_node_id, IS_DESCENDANT_OF] = BitMap()

        # Add direct relationship
        self.relationships[source_node_id, IS_ANCESTOR_OF].add(target_node_id)
        self.relationships[target_node_id, IS_DESCENDANT_OF].add(source_node_id)

    def add_concept(self, concept_id: int, parent_ids: List[int]):
        """Add a concept with its parent relationships."""
        self.nodes.add(concept_id)

        # Initialize relationship BitMaps if they don't exist
        if (concept_id, IS_ANCESTOR_OF) not in self.relationships:
            self.relationships[concept_id, IS_ANCESTOR_OF] = BitMap()
        if (concept_id, IS_DESCENDANT_OF) not in self.relationships:
            self.relationships[concept_id, IS_DESCENDANT_OF] = BitMap()

        for parent_id in parent_ids:
            if not self.exists_node(parent_id):
                self.add_concept(parent_id, [])
            if not self.exists_edge(concept_id, parent_id):
                # Add is_descendant_of relationship
                self.add_edge_with_relationship(
                    concept_id, parent_id, relationship=IS_DESCENDANT_OF
                )

    def exists_edge(self, source_node_id: int, target_node_id: int) -> bool:
        """Check if edge exists between nodes."""
        relationship_key = (source_node_id, IS_ANCESTOR_OF)
        if relationship_key not in self.relationships:
            return False
        return target_node_id in self.relationships[relationship_key]

    def exists_node(self, node_id: int) -> bool:
        """Check if node exists in graph."""
        return node_id in self.nodes

    def get_all_ancestors(self, node_id: int) -> BitMap:
        """Get all ancestors of a node (transitive closure)."""
        if (node_id, IS_ANCESTOR_OF) not in self.relationships:
            return BitMap()

        result = self.relationships[node_id, IS_ANCESTOR_OF].copy()
        queue = list(self.relationships[node_id, IS_ANCESTOR_OF])

        while queue:
            ancestor = queue.pop()
            ancestor_key = (ancestor, IS_ANCESTOR_OF)
            if ancestor_key in self.relationships:
                new_ancestors = self.relationships[ancestor_key] - result
                if new_ancestors:
                    result |= new_ancestors
                    queue.extend(new_ancestors)

        return result

    def get_all_descendants(self, node_id: int) -> BitMap:
        """Get all descendants of a node (transitive closure)."""
        if (node_id, IS_DESCENDANT_OF) not in self.relationships:
            return BitMap()

        result = self.relationships[node_id, IS_DESCENDANT_OF].copy()
        queue = list(self.relationships[node_id, IS_DESCENDANT_OF])

        while queue:
            descendant = queue.pop()
            descendant_key = (descendant, IS_DESCENDANT_OF)
            if descendant_key in self.relationships:
                new_descendants = self.relationships[descendant_key] - result
                if new_descendants:
                    result |= new_descendants
                    queue.extend(new_descendants)

        return result

    def get_relationship_nodes(self, node_id: int, relationship: str) -> BitMap:
        """Get all nodes that have a specific relationship with the given node."""
        relationship_key = (node_id, relationship)
        if relationship_key not in self.relationships:
            return BitMap()
        return self.relationships[relationship_key].copy()

    def get_common_ancestors(self, concept_ids: List[int]) -> BitMap:
        """Find common ancestors of multiple concepts."""
        if not concept_ids:
            return BitMap()

        # get ancestors
        common = self.get_all_ancestors(concept_ids[0])

        # intersection
        for concept_id in concept_ids[1:]:
            common &= self.get_all_ancestors(concept_id)

        return common
