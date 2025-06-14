from dataclasses import dataclass


@dataclass
class Contact:
    owner_user_id: int
    owner_company_id: int
    user_id: int
    company_id: int
    created_at: str


@dataclass
class CompanyRelation:
    company_id: int
    user_id: int
    user_name: str
    user_position: str
    owner_user_id: int
    owner_user_name: str
