from dataclasses import dataclass
from typing import Optional


@dataclass
class SNOMEDConcept:
    id: int
    name: Optional[str]


@dataclass
class RawSNOMEDConcept:
    concept_id: int
    concept_name: Optional[str]
    domain_id: Optional[str]
    vocabulary_id: Optional[str]
    concept_class_id: Optional[str]
    standard_concept: Optional[str]
    concept_code: Optional[str]
    valid_start_date: Optional[str]
    valid_end_date: Optional[str]
    invalid_reason: Optional[str]

    def to_snomed_concept(self) -> SNOMEDConcept:
        return SNOMEDConcept(id=self.concept_id, name=self.concept_name)

    def __hash__(self):
        return hash(self.concept_id)

    def __eq__(self, other):
        if not isinstance(other, RawSNOMEDConcept):
            return NotImplemented
        return self.concept_id == other.concept_id
