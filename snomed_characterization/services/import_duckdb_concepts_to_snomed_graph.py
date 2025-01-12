import duckdb

from pandas import DataFrame

from ..snomed_graph import SNOMEDGraph

q_raw_ancestors = """
    SELECT DISTINCT ancestor_concept_id, 
        descendant_concept_id, 
        min_levels_of_separation, max_levels_of_separation 
    FROM concept_ancestor
    """
q_raw_concepts = "select distinct concept_id from concept"


class ImportDuckDBConceptsToSNOMEDGraph:
    def __init__(self, db_path, snomed_graph: SNOMEDGraph):
        self.db_path = db_path
        self.snomed_graph = snomed_graph

    def _load_concepts_to_df(self) -> DataFrame:
        data = None
        duckdb_conn = duckdb.connect(self.db_path, read_only=True)

        data = duckdb_conn.execute(q_raw_concepts).fetchdf()
        duckdb_conn.close()

        return data

    def _load_concept_ancestors_to_df(self) -> DataFrame:
        data = None
        duckdb_conn = duckdb.connect(self.db_path, read_only=True)

        data = duckdb_conn.execute(q_raw_ancestors).fetchdf()

        duckdb_conn.close()
        return data

    def call(self):
        # process to import the concepts from DuckDB to SNOMED Graph
        concepts_df = self._load_concepts_to_df()
        ancestors_df = self._load_concept_ancestors_to_df()

        for row in concepts_df.itertuples():
            concept_id = row.concept_id
            self.snomed_graph.add_concept(concept_id, parent_ids=[])

        level_one = ancestors_df[ancestors_df["min_levels_of_separation"] == 1]
        for row in level_one.itertuples():
            ancestor_concept_id, descendant_concept_id = (
                row.ancestor_concept_id,
                row.descendant_concept_id,
            )

            self.snomed_graph.add_concept(
                descendant_concept_id, parent_ids=[ancestor_concept_id]
            )

        return concepts_df
