import os
from time import sleep
import requests
from dotenv import load_dotenv

load_dotenv()


def crawl_companies():
    offset = 0
    companies = []
    seen_ids = set()  # 既に見た企業IDを保持するセット

    while True:
        response = requests.get(os.getenv("BASE_URL") + f"/api/cards/?offset={offset}&limit=100")
        offset += 100
        response_json = response.json()

        for company in response_json:
            company_id = company["company_id"]
            # まだ見ていない企業IDの場合のみ追加
            if company_id not in seen_ids:
                seen_ids.add(company_id)
                companies.append(
                    {
                        "company_id": company_id,
                        "company_name": company["company_name"],
                        "company_address": company["address"],
                        "company_phone": company["phone_number"],
                    }
                )

        print(f"offset: {offset}")
        sleep(0.1)
        if offset >= 2000:
            break

    return companies


def save_company_name(companies):
    with open("app/data/companies.csv", "w") as f:
        for company in companies:
            f.write(
                f"{company['company_id']},{company['company_name']},{company['company_address']},{company['company_phone']}\n"
            )


def main():
    companies = crawl_companies()
    save_company_name(companies)


if __name__ == "__main__":
    main()
