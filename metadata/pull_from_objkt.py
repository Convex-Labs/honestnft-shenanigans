import argparse

import pandas as pd
import requests

from honestnft_utils import config

API_URL = "https://data.objkt.com/v2/graphql"
MAX_RECORDS_PAGE = 500


def get_collection_name(contract_address: str):
    """
    Given a contract address, return the collection name from objkt.com
    """
    contract_metadata_query = f'query MyQuery {{ fa(where: {{contract: {{_eq: "{contract_address}"}}}}) {{name}}}}'
    response = requests.post(API_URL, json={"query": contract_metadata_query})
    if response.status_code == 200:
        json_data = response.json()
    else:
        raise Exception(f"Error: {response.status_code},\n{response.text}")

    if (json_data["data"] is None) or (json_data["data"]["fa"] is None):
        return None
    return json_data["data"]["fa"][0]["name"]


def pull_from_objkt(contract_address: str) -> list:
    """
    Given a contract address, return the metadata from objkt.com
    """
    offset_variable = 0
    pages = []
    new_results = True

    while new_results:
        query_part_1 = f'query MyQuery($offset: Int = {offset_variable}, $_eq: String = "{contract_address}") {{'
        query_part_2 = """
            token(where: {fa: {contract: {_eq: $_eq}}, name: {_is_null: false}}, order_by: {token_id: asc}, offset: $offset) {
            token_id
            name
            attributes {
                attribute {
                value
                name
                }
            }
            }
        }
        """
        response = requests.post(
            API_URL,
            json={"query": query_part_1 + query_part_2},
        )
        offset_variable += MAX_RECORDS_PAGE
        if response.status_code == 200:
            json_data = response.json()
        else:
            raise Exception(f"Error: {response.status_code},\n{response.text}")

        pages.append(json_data)
        if len(json_data["data"]["token"]) < MAX_RECORDS_PAGE:
            new_results = False

    metadata_list = []
    for page in pages:
        for row in page["data"]["token"]:
            token = {"TOKEN_ID": row["token_id"], "TOKEN_NAME": row["name"]}
            for value in row["attributes"]:
                token[value["attribute"]["name"]] = value["attribute"]["value"]
            metadata_list.append(token)
    return metadata_list


def pull_metadata(contract_address: str):
    collection_name = get_collection_name(contract_address)
    if collection_name is None:
        return "Contract not found"

    collection_name.replace(" ", "_")

    # Fetch all attribute records from the remote server
    records = pull_from_objkt(contract_address)

    # Generate traits DataFrame and save to disk as csv
    trait_db = pd.DataFrame(records)

    if trait_db.duplicated().any():
        print("Duplicates found, removing...")
        trait_db.drop_duplicates(inplace=True)

    trait_db["TOKEN_ID"] = pd.to_numeric(trait_db["TOKEN_ID"])

    trait_db.sort_values(by=["TOKEN_ID"], inplace=True, ascending=True)
    trait_db.set_index("TOKEN_ID", inplace=True)
    print(trait_db.head())
    trait_db.to_csv(f"{config.ATTRIBUTES_FOLDER}/{collection_name}.csv")


if __name__ == "__main__":
    # Parse command line arguments
    ARG_PARSER = argparse.ArgumentParser(
        description="Download Tezos NFT metadata from OBJKT.com"
    )
    ARG_PARSER.add_argument(
        "-contract",
        type=str,
        required=True,
        default=None,
        help="Collection contract address",
    )

    ARGS = ARG_PARSER.parse_args()

    pull_metadata(ARGS.contract)
