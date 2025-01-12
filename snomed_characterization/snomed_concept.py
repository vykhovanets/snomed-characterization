from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SNOMEDConcept:
    id: int
    name: Optional[str]
    # parents: Optional[List[SNOMEDConcept]]
    # children: Optional[List[SNOMEDConcept]]


@dataclass
class RawSNOMEDConcept:
    concept_id: int
    concept_name: str
    domain_id: str
    vocabulary_id: str
    concept_class_id: str
    standard_concept: str
    concept_code: str
    valid_start_date: str
    valid_end_date: str
    invalid_reason: str

    def to_snomed_concept(self) -> SNOMEDConcept:
        return SNOMEDConcept(id=self.concept_id, name=self.concept_name)
