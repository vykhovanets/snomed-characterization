from collections import deque
from pyroaring import BitMap

# from .import_duckdb_concepts_base import ImportDuckDBConceptsBase
from snomed_characterization.services.import_duckdb_concepts_base import (
    ImportDuckDBConceptsBase,
)
from snomed_characterization.graphs.bitmap_graph import BitMapGraph


class ImportDuckDBConceptsToBitMapGraph(ImportDuckDBConceptsBase):
    def __init__(self, db_path):
        super().__init__(db_path, None)

        self.snomed_graph = BitMapGraph()

    def call(self):
        """Import concepts and build graph using BitMap for efficient storage."""
        missing_concepts = BitMap()

        # Load initial concept IDs
        people_concepts_df = self._load_people_concepts_to_df()
        initial_concepts = BitMap(people_concepts_df["condition_concept_id"].unique())
        queue = deque(initial_concepts)

        # Load all concepts with their ancestors
        concepts_df = self._load_concepts_to_df().set_index("concept_id")

        while queue:
            concept_id = queue.popleft()
            try:
                concept_row = concepts_df.loc[concept_id]
                ancestors = concept_row["level_1_ancestors"]
                # Convert ancestors to integers and create BitMap
                ancestor_ids = BitMap([int(ancestor) for ancestor in ancestors])

                # Add concept and its ancestors to graph
                self.snomed_graph.add_concept(concept_id, ancestor_ids)

                # Add new ancestors to queue (ones we haven't processed yet)
                new_ancestors = ancestor_ids - self.snomed_graph.nodes
                queue.extend(new_ancestors)

            except KeyError:
                missing_concepts.add(concept_id)
                self.snomed_graph.add_concept(concept_id, BitMap())

        print(f"Missing concepts: {missing_concepts}")
        print(f"Total concepts in graph: {len(self.snomed_graph.nodes)}")
        print("Finished creating graph")

        return concepts_df

    def get_concept_ancestors(self, concept_id: int) -> BitMap:
        """Get all ancestors for a given concept."""
        return self.snomed_graph.get_all_ancestors(concept_id)

    def get_concept_descendants(self, concept_id: int) -> BitMap:
        """Get all descendants for a given concept."""
        return self.snomed_graph.get_all_descendants(concept_id)

    def get_common_ancestors(self, concept_ids: list[int]) -> BitMap:
        """Get common ancestors for a list of concepts."""
        if not concept_ids:
            return BitMap()

        # Get ancestors for first concept
        common = self.snomed_graph.get_all_ancestors(concept_ids[0])

        # Intersect with ancestors of remaining concepts
        for concept_id in concept_ids[1:]:
            common &= self.snomed_graph.get_all_ancestors(concept_id)
        return common
