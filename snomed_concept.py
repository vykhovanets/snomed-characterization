from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SNOMEDConcept:
    id: str
    parents: Optional[List[str]]
    children: Optional[List[str]]
