import duckdb

import pandas as pd

from pandas import DataFrame

from snomed_characterization.graphs.snomed_complete_graph import SNOMEDCompleteGraph
from snomed_characterization.snomed_concept import RawSNOMEDConcept

from snomed_characterization.duckdb.queries import q_concepts


class ImportDuckDBConceptsToCompleteSNOMEDGraph:
    def __init__(self, db_path, snomed_graph: SNOMEDCompleteGraph):
        self.db_path = db_path
        self.snomed_graph = snomed_graph

    def _load_concepts_to_df(self) -> DataFrame:
        data = None
        duckdb_conn = duckdb.connect(self.db_path, read_only=True)

        data = duckdb_conn.execute(q_concepts).fetchdf()
        duckdb_conn.close()

        return data

    def call(self):
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
