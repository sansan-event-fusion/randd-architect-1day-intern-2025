import requests

from .models import BusinessCardResponse, SimilarBusinessCardResponse


class BusinessCardCRUD:
    def __init__(self):
        from app.config import get_settings

        self.base_url = get_settings().API_BASE_URL

    def get_all_cards(self, offset: int = 0, limit: int = 100) -> list[BusinessCardResponse]:
        """Get all business cards with pagination."""
        response = requests.get(
            f"{self.base_url}/cards/",
            params={"offset": offset, "limit": limit},
            timeout=30,
        )
        response.raise_for_status()
        return [BusinessCardResponse(**card) for card in response.json()]

    def get_card_by_user_id(self, user_id: int) -> BusinessCardResponse:
        """Get a specific business card by user ID."""
        response = requests.get(f"{self.base_url}/cards/{user_id}", timeout=30)
        response.raise_for_status()
        return BusinessCardResponse(**response.json())

    def get_cards_count(self) -> int:
        """Get total count of business cards."""
        response = requests.get(f"{self.base_url}/cards/count", timeout=30)
        response.raise_for_status()
        return response.json()

    def get_similar_users(self, user_id: int) -> list[SimilarBusinessCardResponse]:
        """Get top 10 similar users for a given user ID."""
        response = requests.get(
            f"{self.base_url}/cards/{user_id}/similar_top10_users",
            timeout=30,
        )
        response.raise_for_status()
        return [SimilarBusinessCardResponse(**card) for card in response.json()]
