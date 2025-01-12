import unittest
from unittest.mock import patch, Mock
import pandas as pd

from snomed_characterization.snomed_graph import SNOMEDGraph
from snomed_characterization.services.import_duckdb_concepts_to_snomed_graph import (
    ImportDuckDBConceptsToSNOMEDGraph,
)


class TestImportDuckDBConceptsToSNOMEDGraph(unittest.TestCase):
    def setUp(self):
        self.mock_db_path = "test_db.duckdb"
        self.mock_snomed_graph = Mock(spec=SNOMEDGraph)
        self.importer = ImportDuckDBConceptsToSNOMEDGraph(
            self.mock_db_path, self.mock_snomed_graph
        )

    @patch("duckdb.connect")
    def test_load_concepts_to_df(self, mock_connect):
        mock_connection = Mock()
        mock_connection.execute.return_value.fetchdf.return_value = pd.DataFrame(
            {"concept_id": [1, 2, 3]}
        )
        mock_connect.return_value = mock_connection
        df = self.importer._load_concepts_to_df()
        self.assertEqual(len(df), 3)
        mock_connect.assert_called_once_with(self.mock_db_path, read_only=True)

    @patch("duckdb.connect")
    def test_call(self, mock_connect):
        mock_connection = Mock()
        mock_connection.execute.return_value.fetchdf.return_value = pd.DataFrame(
            {"concept_id": [1, 2, 3]}
        )
        mock_connect.return_value = mock_connection
        self.importer.call()
        self.mock_snomed_graph.add_concept.assert_has_calls(
            [
                unittest.mock.call(1, parent_ids=[]),
                unittest.mock.call(2, parent_ids=[]),
                unittest.mock.call(3, parent_ids=[]),
            ]
        )
