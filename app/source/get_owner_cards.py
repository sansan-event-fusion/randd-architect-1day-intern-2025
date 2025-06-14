import requests
import pandas as pd

def get_owner_cards(owner_id: str) -> pd.DataFrame:
    """
    Fetches the owner cards for a given owner ID.

    Args:
        owner_id (str): The ID of the owner whose cards are to be fetched.

    Returns:
        dict: The JSON response containing the owner cards.
    """
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{owner_id}'
    headers = {'accept': 'application/json'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching owner cards: {response.status_code} - {response.text}")
    
    df = pd.DataFrame(response.json())

    return df

def main():
    owner_id = '9230809757'  # Example owner ID
    try:
        df = get_owner_cards(owner_id)
        print("Owner cards fetched successfully.")
        print(df.head())
        print(f"Total cards for owner {owner_id}: {len(df)}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()