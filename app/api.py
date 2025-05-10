
import requests
from datatype import BusinessCard, ExchangeHistory
from yarl import URL


class BaseRequest:
    def __init__(self, api_root: str):
        self.str_api_root = URL(api_root)

    def _requesting(self, ad_str:str)->requests.Response:
        try:
            url = self.str_api_root / ad_str
            response = requests.get(f"{url}")
            return response
        except Exception as e:
            print(f"エラーが発生しました: {e}")

class BuisinessCardAPI(BaseRequest):
    def __init__(self, str_api_root:str) ->None:
        super().__init__(str_api_root)

    def get_all_cards(self)->list[BusinessCard]:
        response = self._requesting("cards/")
        cards_data = response.json()
        cards:list[BusinessCard] = [BusinessCard(**card) for card in cards_data]
        return cards

    def get_similar_users(self, user_id:str)->list[BusinessCard]:
        response = self._requesting(f"cards/{user_id}/similar_top10_users")
        cards_data = response.json()
        cards:list[BusinessCard] = [BusinessCard(**card) for card in cards_data]
        return cards


