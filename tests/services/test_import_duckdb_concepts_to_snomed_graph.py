import unittest
from unittest.mock import patch, Mock
import pandas as pd

from snomed_characterization.snomed_graph import SNOMEDGraph
from snomed_characterization.services.import_duckdb_concepts_to_snomed_graph import (
    ImportDuckDBConceptsToSNOMEDGraph,
)

q_concepts = """
    select * from concept c 
    left join concept_ancestor ca
    on c.concept_id=ca.descendant_concept_id
    where c.invalid_reason is  null
    AND ca.min_levels_of_separation=1
    and standard_concept is not null
"""


class TestImportDuckDBConceptsToSNOMEDGraph(unittest.TestCase):
    @patch("duckdb.connect")
    def test_call_method(self, mock_connect):
        # mocked data
        mock_concepts_df = pd.DataFrame(
            {
                "concept_id": [1, 2, 3],
                "ancestor_concept_id": [None, 2, 3],
                "descendant_concept_id": [1, 2, 3],
                "min_levels_of_separation": [1, 2, 1],
                "max_levels_of_separation": [1, 2, 1],
            }
        )

        # mock connection
        mock_connection = Mock()
        mock_connection.execute.side_effect = [
            Mock(fetchdf=Mock(return_value=mock_concepts_df)),
        ]
        mock_connect.return_value = mock_connection

        # graph
        mock_snomed_graph = Mock()
        mock_snomed_graph.add_concept.return_value = None

        # Initialize service
        importer = ImportDuckDBConceptsToSNOMEDGraph("mock_db_path", mock_snomed_graph)

        # Call the method
        result = importer.call()

        # Assertions for concepts DataFrame
        pd.testing.assert_frame_equal(result, mock_concepts_df)

        # Ensure the execute method was called with the correct queries
        mock_connection.execute.assert_any_call(q_concepts)

        # Validate SNOMEDGraph interactions
        # mock_snomed_graph.add_concept.assert_any_call(2, parent_ids=[2])

        # Check connection close was called
        self.assertEqual(mock_connection.close.call_count, 1)
