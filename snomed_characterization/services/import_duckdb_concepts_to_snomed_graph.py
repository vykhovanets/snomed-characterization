import duckdb
import pandas as pd

from pandas import DataFrame

from ..snomed_graph import SNOMEDGraph

q_concepts = """
    select * from concept c 
    left join concept_ancestor ca
    on c.concept_id=ca.descendant_concept_id
    where c.invalid_reason is  null
    AND ca.min_levels_of_separation=1
    and standard_concept is not null
    and domain_id='Condition'
"""


class ImportDuckDBConceptsToSNOMEDGraph:
    def __init__(self, db_path, snomed_graph: SNOMEDGraph):
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

        for row in concepts_df.itertuples():
            concept_id = row.concept_id
            ancestor_concept_id = row.ancestor_concept_id
            parent_ids = []

            if not pd.isna(ancestor_concept_id):
                parent_ids.append(int(ancestor_concept_id))

            # XXX: debug the test call
            self.snomed_graph.add_concept(concept_id, parent_ids)

        return concepts_df
