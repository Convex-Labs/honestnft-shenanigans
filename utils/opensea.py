import time

import requests

from utils import config

SLEEP = 5


def get_opensea_events(
    contract_address,
    account_address=None,
    continuous=True,
    cursor=None,
    event_type=None,
    have=[],
    limit=300,
    occurred_before=None,
    only_opensea=False,
    token_id=None,
):
    """
    API wrapper for the OpenSea events API.
    https://docs.opensea.io/reference/retrieving-asset-events

    :param contract_address: The NFT contract address for the assets for which to show events.
    :type contract_address: str
    :param account_address: A user account's wallet address to filter for events on an account.
    :type account_address: str
    :param continuous: Return only first page of events or try to fetch all pages.
    :type continuous: bool
    :param cursor: A cursor pointing to the page to retrieve.
    :type cursor: str
    :param event_type: The event type to filter. Can be "created" for new auctions, "successful" for sales, "cancelled", "bid_entered", "bid_withdrawn", "transfer", or "approve".
    :type event_type: str
    :param have: List of already fetched events. Used internally to paginate trough events.
    :type have: list
    :param limit: Maximum number of events to fetch per request.
    :type limit: int
    :param occurred_before: Only show events listed before this timestamp. Seconds since the Unix epoch.
    :type occurred_before: datetime.datetime
    :param only_opensea: Restrict to events on OpenSea auctions.
    :type only_opensea: bool
    :param token_id: The token's id to optionally filter by.
    :type token_id: int

    :return: A list of events.
    :rtype: list
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

    response = requests.request("GET", url, headers=headers, params=querystring)

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
