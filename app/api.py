import requests
from datatype import BusinessCard, ExchangeHistory
from yarl import URL


class BaseRequest:
    def __init__(self, api_root: str):
        self.str_api_root = URL(api_root)

    def _requesting(self, ad_str: str, params=None) -> requests.Response | None:
        try:
            url = self.str_api_root / ad_str
            response = requests.get(f"{url}", params=params, timeout=10)
        except requests.Timeout:
            return None
        return response


class BusinessCardAPI(BaseRequest):
    def __init__(self, str_api_root: str) -> None:
        super().__init__(str_api_root)

    def get_all_cards(self) -> list[BusinessCard]:
        response = self._requesting("cards/", {"limit": self.get_card_count()})
        cards_data = response.json()
        cards: list[BusinessCard] = [BusinessCard(**card) for card in cards_data]
        return cards

    def get_card_count(self) -> int:
        response = self._requesting("cards/count")
        count = int(response.text)
        return count

    def get_similar_users(self, user_id: str) -> list[BusinessCard]:
        response = self._requesting(f"cards/{user_id}/similar_top10_users")
        cards_data = response.json()
        cards: list[BusinessCard] = [BusinessCard(**card) for card in cards_data]
        return cards

    def get_all_contacts(self) -> list[ExchangeHistory]:
        response = self._requesting("contacts/", {"limit": self.get_card_count()})
        cards_data = response.json()
        cards: list[ExchangeHistory] = [ExchangeHistory(**card) for card in cards_data]
        return cards

    def get_contact_count(self) -> int:
        response = self._requesting("contacts/count")
        count = int(response.text)
        return count
