import duckdb
import pandas as df

from ..snomed_graph import SNOMEDGraph


class ImportDuckDBConceptsToSNOMEDGraph:
    def __init__(self, db_path, snomed_graph: SNOMEDGraph):
        self.db_path = db_path
        self.snomed_graph = snomed_graph

    def _load_concepts_to_df(self) -> df.DataFrame:
        data = None
        duckdb_conn = duckdb.connect(self.db_path, read_only=True)

        data = duckdb_conn.execute("SELECT * FROM concept").fetchdf()
        duckdb_conn.close()

        return data

    def call(self):
        # process to import the concepts from DuckDB to SNOMED Graph
        concepts_df = self._load_concepts_to_df()

        for row in concepts_df.itertuples():
            concept_id = row.concept_id
            self.snomed_graph.add_concept(concept_id, parent_ids=[])

        return concepts_df


g = SNOMEDGraph()
importer_service = ImportDuckDBConceptsToSNOMEDGraph(
    "data/my_sampled_cdm_v1_0.duckdb", g
)

df = importer_service.call()

df.head()
