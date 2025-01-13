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
    ancestor_concept_id: Optional[int]
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

    def __hash__(self):
        return hash(self.concept_id)

    def __eq__(self, other):
        if not isinstance(other, RawSNOMEDConcept):
            return NotImplemented
        return self.concept_id == other.concept_id
