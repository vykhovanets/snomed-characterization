import pandas as pd
from pandas import DataFrame
from collections import deque

from snomed_characterization.graphs.snomed_complete_graph_builder import (
    SNOMEDCompleteGraphBuilder,
)

from snomed_characterization.snomed_concept import RawSNOMEDConcept

# from .import_duckdb_concepts_base import ImportDuckDBConceptsBase
from snomed_characterization.services.import_duckdb_concepts_base import (
    ImportDuckDBConceptsBase,
)


class ImportDuckDBConceptsToCompleteSNOMEDGraph(ImportDuckDBConceptsBase):
    def _get_raw_ancestors_from_df(self, df: DataFrame, columns, ancestor_ids):
        result = []
        for ancestor_id in ancestor_ids:
            try:
                ancestor_row = df.loc[ancestor_id]
                concept_dict = {
                    **ancestor_row[columns].to_dict(),
                    "concept_id": ancestor_id,
                }
                raw_ancestor = RawSNOMEDConcept(**concept_dict)
                result.append(raw_ancestor)
            except KeyError:
                # print(f"Missing ancestor {ancestor_id}")
                continue

        return result

    def call(self):
        self.snomed_graph: SNOMEDCompleteGraphBuilder

        missing_concepts = set()
        people_concepts_df = self._load_people_concepts_to_df()
        queue = deque(people_concepts_df["condition_concept_id"].unique())

        concepts_df = self._load_concepts_to_df().set_index("concept_id")

        needed_columns = list(RawSNOMEDConcept.__annotations__.keys())
        needed_columns.remove("concept_id")

        while queue:
            concept_id = queue.popleft()

            try:
                concept_row = concepts_df.loc[concept_id]
                concept_dict = {
                    **concept_row[needed_columns].to_dict(),
                    "concept_id": concept_id,
                }

                raw_concept = RawSNOMEDConcept(**concept_dict)
            except KeyError:
                missing_concepts.add(concept_id)
                continue

            ancestors = concept_row["level_1_ancestors"]
            ancestors = [int(ancestor) for ancestor in ancestors]
            raw_ancestors = self._get_raw_ancestors_from_df(
                concepts_df, needed_columns, ancestors
            )

            self.snomed_graph.add_concept(raw_concept, raw_ancestors)
            queue.extend(ancestors)

        return concepts_df

    # XXX: deprecated since we just want the conditions related to the people in the sample db
    def call_deprecated(self):
        # process to import the concepts from DuckDB to SNOMED Graph
        concepts_df = self._load_concepts_to_df()
        graph = self.snomed_graph.graph
        needed_columns = list(RawSNOMEDConcept.__annotations__.keys())

        filtered_df = concepts_df[needed_columns]

        concepts = [
            RawSNOMEDConcept(**row.to_dict()) for _, row in filtered_df.iterrows()
        ]

        [self.snomed_graph.add_concept(concept, parent_ids=[]) for concept in concepts]

        # Build edges list first
        edges_to_add = []
        for _, node_data in graph.nodes(data=True):
            concept = node_data["data"]
            if not pd.isna(concept.ancestor_concept_id):
                edges_to_add.append((concept.ancestor_concept_id, concept.concept_id))

        graph.add_edges_from(edges_to_add)

        return concepts_df
