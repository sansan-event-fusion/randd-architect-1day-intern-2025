from datetime import datetime

import requests

from .models import ContactHistoryResponse


class ContactHistoryCRUD:
    def __init__(self):
        try:
            # テスト実行時のabsolute import
            from app.config import get_settings
        except ImportError:
            # Streamlit実行時のrelative import
            from config import get_settings

        self.base_url = get_settings().API_BASE_URL

    def get_all_contacts(
        self,
        offset: int = 0,
        limit: int = 100,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[ContactHistoryResponse]:
        """Get all contact histories with pagination and optional date filtering."""
        params = {"offset": offset, "limit": limit}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = requests.get(f"{self.base_url}/contacts/", params=params, timeout=30)
        response.raise_for_status()
        return [ContactHistoryResponse(**contact) for contact in response.json()]

    def get_contacts_count(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Get total count of contact histories with optional date filtering."""
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = requests.get(f"{self.base_url}/contacts/count", params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_contacts_by_owner_user(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 100,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[ContactHistoryResponse]:
        """Get contact histories by owner user ID."""
        params = {"offset": offset, "limit": limit}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = requests.get(
            f"{self.base_url}/contacts/owner_user/{user_id}",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return [ContactHistoryResponse(**contact) for contact in response.json()]

    def get_contacts_by_owner_company(
        self,
        company_id: int,
        offset: int = 0,
        limit: int = 100,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[ContactHistoryResponse]:
        """Get contact histories by owner company ID."""
        params = {"offset": offset, "limit": limit}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = requests.get(
            f"{self.base_url}/contacts/owner_company/{company_id}",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return [ContactHistoryResponse(**contact) for contact in response.json()]
