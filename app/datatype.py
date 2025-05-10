from dataclasses import dataclass
from datetime import datetime


@dataclass
class BusinessCard:
    user_id: int
    company_id: int
    full_name: str
    position: str
    company_name: str
    address: str
    phone_number: str
    similarity: float | None = None


@dataclass
class ExchangeHistory:
    owner_user_id: int  # 名刺所有者のユーザID
    owner_company_id: int  # 名刺所有者の会社ID
    user_id: int  # 名刺記載ユーザのユーザID
    company_id: int  # 名刺記載ユーザの会社ID
    created_at: datetime
