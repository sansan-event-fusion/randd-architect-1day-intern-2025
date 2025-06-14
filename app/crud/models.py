from datetime import datetime

from pydantic import BaseModel


class BusinessCardResponse(BaseModel):
    user_id: int
    company_id: int
    full_name: str
    company_name: str
    address: str
    phone_number: str


class SimilarBusinessCardResponse(BaseModel):
    user_id: int
    company_id: int
    full_name: str
    company_name: str
    address: str
    phone_number: str
    similarity: float


class ContactHistoryResponse(BaseModel):
    contact_id: int
    owner_user_id: int
    target_user_id: int
    contact_datetime: datetime
    owner_company_id: int
    target_company_id: int
    contact_type: str
    notes: str | None = None
