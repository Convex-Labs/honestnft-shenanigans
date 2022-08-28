from typing import List, Optional

import requests

from honestnft_utils import config


def get_all_token_ids(
    contract_address: str, _offset_token_id: Optional[str] = None, _have: List[int] = []
) -> List[int]:
    """Get all token IDs for a given NFT contract.

    :param contract_address: Contract address
    :param _start_token_id: Offset token ID used for pagination. (Used internally)
    :param _have: List of already fetched token_ids. (Used internally)
    :return: A list of all token_ids for the given contract.
    """
    all_data = []

    all_data.extend(_have)

    url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{config.ALCHEMY_API_KEY}/getNFTsForCollection"

    query = {
        "contractAddress": contract_address,
        "withMetadata": "false",
        "limit": "100",
        "startToken": _offset_token_id,
    }
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, params=query)
    if response.status_code == 200:
        decoded_response = response.json()
        for entry in decoded_response["nfts"]:
            all_data.append(int(entry["id"]["tokenId"], 0))

        if decoded_response.get("nextToken"):
            return get_all_token_ids(
                contract_address=contract_address,
                _offset_token_id=decoded_response["nextToken"],
                _have=all_data,
            )
        else:
            return all_data
    else:
        print(response.text)
        raise Exception(f"Failed to get token IDs for contract {contract_address}")
