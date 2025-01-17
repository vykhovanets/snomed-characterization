import duckdb
from typing import Union, Optional
from pandas import DataFrame

from snomed_characterization.graphs.snomed_complete_graph_builder import (
    SNOMEDCompleteGraphBuilder,
)
from snomed_characterization.graphs.snomed_graph_builder import SNOMEDGraphBuilder

from snomed_characterization.duckdb.queries import q_concepts, q_people_concepts


class ImportDuckDBConceptsBase:
    def __init__(
        self,
        db_path,
        snomed_graph: Optional[Union[SNOMEDCompleteGraphBuilder, SNOMEDGraphBuilder]],
    ):
        self.db_path = db_path
        self.snomed_graph = snomed_graph

    def _load_concepts_to_df(self) -> DataFrame:
        data = None
        duckdb_conn = duckdb.connect(self.db_path, read_only=True)

        data = duckdb_conn.execute(q_concepts).fetchdf()
        duckdb_conn.close()

        return data

    def _load_people_concepts_to_df(self) -> DataFrame:
        data = None
        duckdb_conn = duckdb.connect(self.db_path, read_only=True)

        data = duckdb_conn.execute(q_people_concepts).fetchdf()
        duckdb_conn.close()

        return data

    def call(self):
        raise NotImplementedError("Method not implemented")
