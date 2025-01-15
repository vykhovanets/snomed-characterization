import pandas as pd
from collections import deque

from snomed_characterization.graphs.snomed_graph_builder import SNOMEDGraphBuilder
from .import_duckdb_concepts_base import ImportDuckDBConceptsBase


class ImportDuckDBConceptsToSNOMEDGraph(ImportDuckDBConceptsBase):
    def call(self):
        self.snomed_graph: SNOMEDGraphBuilder
        missing_concepts = set()
        people_concepts_df = self._load_people_concepts_to_df()
        queue = deque(people_concepts_df["condition_concept_id"].unique())

        concepts_df = self._load_concepts_to_df().set_index("concept_id")

        while queue:
            concept_id = queue.popleft()

            # get ancestors
            try:
                concept_row = concepts_df.loc[concept_id]
            except KeyError:
                missing_concepts.add(concept_id)
                self.snomed_graph.add_concept(concept_id, [])
                continue

            ancestors = concept_row["level_1_ancestors"]
            ancestors = [int(ancestor) for ancestor in ancestors]

            self.snomed_graph.add_concept(concept_id, ancestors)
            queue.extend(ancestors)

        print(f"Missing concepts: {missing_concepts}")
        print("Finished creating graph")

        return concepts_df

    # XXX: deprecated since we just want the conditions related to the people in the sample db
    def call_deprecated(self):
        concepts_df = self._load_concepts_to_df()

        all_concepts = pd.concat(
            [concepts_df["concept_id"], concepts_df["ancestor_concept_id"].dropna()]
        ).unique()

        for concept in all_concepts:
            self.snomed_graph.add_concept(int(concept), [])

        # Then add edges level by level
        for level in sorted(concepts_df["min_levels_of_separation"].unique()):
            level_relationships = concepts_df[
                concepts_df["min_levels_of_separation"] == level
            ]

            for row in level_relationships.itertuples():
                concept_id = row.concept_id  # type: ignore
                ancestor_concept_id = row.ancestor_concept_id  # type: ignore
                if not pd.isna(ancestor_concept_id):
                    parent_ids = [int(ancestor_concept_id)]
                    self.snomed_graph.add_concept(concept_id, parent_ids)

        return concepts_df
