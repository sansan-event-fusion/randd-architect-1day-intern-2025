import requests
import pandas as pd

def get_cards() -> pd.DataFrame:
    """
    Fetches the owner cards for a given owner ID.

    Args:
        owner_id (str): The ID of the owner whose cards are to be fetched.

    Returns:
        dict: The JSON response containing the owner cards.
    """
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/'
    headers = {'accept': 'application/json'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching owner cards: {response.status_code} - {response.text}")
    
    return pd.DataFrame(response.json())

def main():
    try:
        df = get_cards()
        print("Cards fetched successfully.")
        print(df.head())
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()