import duckdb
from typing import List

from snomed_characterization.snomed_concept import RawSNOMEDConcept

q_concepts = """
    SELECT concept_id, concept_name,
       domain_id,
   vocabulary_id,
concept_class_id,
standard_concept,
    concept_code,
valid_start_date,
  valid_end_date,
  invalid_reason
  FROM concept
    """


class LoadSNOMEDConceptsFromDuckdb:
    def __init__(self, db_path):
        self.db_path = db_path

    def call(self) -> List[RawSNOMEDConcept]:
        concepts_df = self._load_concepts()

        data = [RawSNOMEDConcept(**row.to_dict()) for _, row in concepts_df.iterrows()]

        return data

    def _load_concepts(self):
        db_conn = duckdb.connect(self.db_path, read_only=True)
        df = db_conn.execute(q_concepts).fetchdf()
        db_conn.close()

        return df
