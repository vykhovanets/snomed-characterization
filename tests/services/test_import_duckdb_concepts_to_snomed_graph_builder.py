import unittest
from unittest.mock import patch, Mock, call
import pandas as pd

from snomed_characterization.services.import_duckdb_concepts_to_snomed_graph import (
    ImportDuckDBConceptsToSNOMEDGraph,
)

q_concepts = """
    WITH grouped_ancestors AS (
        SELECT 
            descendant_concept_id,
            ARRAY_AGG(ancestor_concept_id ORDER BY ancestor_concept_id) as level_1_ancestors
        FROM concept_ancestor ca
        WHERE min_levels_of_separation = 1
        GROUP BY descendant_concept_id
    )
    SELECT 
        c.*,
        ga.level_1_ancestors
    FROM concept c
    INNER JOIN grouped_ancestors ga ON c.concept_id = ga.descendant_concept_id
    WHERE c.invalid_reason IS NULL 
        AND c.standard_concept = 'S'
        AND c.domain_id = 'Condition';
    """

q_people_concepts = """
    select distinct condition_concept_id
    from condition_occurrence;
    """


class TestImportDuckDBConceptsToSNOMEDGraphBuilder(unittest.TestCase):
    @patch("duckdb.connect")
    def test_call_method(self, mock_connect):
        # mocked data

        mock_people_concepts_df = pd.DataFrame(
            {
                "condition_concept_id": [1, 2, 3],
            }
        )
        mock_concepts_df = pd.DataFrame(
            {
                "concept_id": [1, 2, 3],
                "descendant_concept_id": [1, 2, 3],
                "min_levels_of_separation": [1, 2, 1],
                "max_levels_of_separation": [1, 2, 1],
                "level_1_ancestors": [[4, 5], [], []],
            }
        )

        # mock connection
        mock_connection = Mock()
        mock_connection.execute.side_effect = [
            Mock(fetchdf=Mock(return_value=mock_people_concepts_df)),
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

        indexed_mock_concepts_df = mock_concepts_df.set_index("concept_id")

        # Assertions for concepts DataFrame
        pd.testing.assert_frame_equal(result, indexed_mock_concepts_df)

        # Ensure the execute method was called with the correct queries
        pd.testing.assert_frame_equal(result, indexed_mock_concepts_df)

        mock_connection.execute.assert_has_calls(
            [call(q_people_concepts), call(q_concepts)], any_order=False
        )

        # Validate SNOMEDGraph interactions
        # mock_snomed_graph.add_concept.assert_any_call(2, parent_ids=[2])

        # Check connection close was called
        self.assertEqual(mock_connection.close.call_count, 2)
