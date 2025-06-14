from dataclasses import dataclass


@dataclass
class OtherCompanyMember:
    id: int
    company_id: int
    name: str
    position: str
    relationship: str
