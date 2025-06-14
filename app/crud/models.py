from datetime import datetime

from pydantic import BaseModel


class BusinessCardResponse(BaseModel):
    user_id: str
    company_id: str
    full_name: str
    company_name: str
    address: str
    phone_number: str


class SimilarBusinessCardResponse(BaseModel):
    user_id: str
    company_id: str
    full_name: str
    company_name: str
    address: str
    phone_number: str
    similarity: float


class ContactHistoryResponse(BaseModel):
    owner_user_id: str
    owner_company_id: str
    user_id: str
    company_id: str
    created_at: datetime

    @property
    def target_user_id(self) -> str:
        return self.user_id

    @property
    def target_company_id(self) -> str:
        return self.company_id

    @property
    def contact_datetime(self) -> datetime:
        return self.created_at
