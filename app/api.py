# %%
import logging
from typing import Any

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def get_business_cards(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    """ビジネスカードを取得する関数"""
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/"
    params = {"offset": offset, "limit": limit}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    cards = get_business_cards(limit=5)

    logger.info("取得したカード:")
    for card in cards:
        logger.info(card)

# %%
