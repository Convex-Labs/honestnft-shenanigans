import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from honestnft_utils import config

SLEEP = 5


def get_opensea_events(
    contract_address: str,
    account_address: Optional[str] = None,
    continuous: bool = True,
    cursor: Optional[str] = None,
    event_type: Optional[str] = None,
    have: list = [],
    limit: int = 300,
    occurred_before: Optional[str] = None,
    only_opensea: bool = False,
    token_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    API wrapper for the OpenSea events API.
    https://docs.opensea.io/reference/retrieving-asset-events

    :param contract_address: The NFT contract address for the assets for which to show events.
    :param account_address: A user account's wallet address to filter for events on an account.
    :param continuous: Return only first page of events or try to fetch all pages.
    :param cursor: A cursor pointing to the page to retrieve.
    :param event_type: The event type to filter. Can be "created" for new auctions, "successful" for sales, "cancelled", "bid_entered", "bid_withdrawn", "transfer", or "approve".
    :param have: List of already fetched events. Used internally to paginate trough events.
    :param limit: Maximum number of events to fetch per request.
    :param occurred_before: Only show events listed before this timestamp. Seconds since the Unix epoch.
    :param only_opensea: Restrict to events on OpenSea auctions.
    :param token_id: The token's id to optionally filter by.

    :return: A list of events.
    """
    all_data = []

    all_data.extend(have)
    url = "https://api.opensea.io/api/v1/events"

    querystring = {
        "account_address": account_address,
        "asset_contract_address": contract_address,
        "cursor": cursor,
        "event_type": event_type,
        "limit": limit,
        "occurred_before": occurred_before,
        "only_opensea": only_opensea,
        "token_id": token_id,
    }

    headers = {"Accept": "application/json", "X-API-KEY": config.OPENSEA_API_KEY}

    response = requests.request("GET", url, headers=headers, params=querystring)  # type: ignore

    if response.status_code == 200:
        decode_response = response.json()
        events = decode_response["asset_events"]
        all_data.extend(events)

        if decode_response["next"] is not None and continuous is True:
            return get_opensea_events(
                contract_address=contract_address,
                account_address=account_address,
                continuous=continuous,
                cursor=decode_response["next"],
                event_type=event_type,
                have=all_data,
                limit=limit,
                occurred_before=occurred_before,
                only_opensea=only_opensea,
                token_id=token_id,
            )
        else:
            return all_data

    else:
        print(response.text)
        print("error, sleeping then calling again")
        time.sleep(SLEEP * 5)
        return get_opensea_events(
            contract_address=contract_address,
            account_address=account_address,
            continuous=continuous,
            cursor=cursor,
            event_type=event_type,
            have=all_data,
            limit=limit,
            occurred_before=occurred_before,
            only_opensea=only_opensea,
            token_id=token_id,
        )
