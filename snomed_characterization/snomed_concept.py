from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SNOMEDConcept:
    id: int
    name: Optional[str]
    # parents: Optional[List[SNOMEDConcept]]
    # children: Optional[List[SNOMEDConcept]]
