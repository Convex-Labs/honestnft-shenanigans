import argparse
import logging
import multiprocessing
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

from honestnft_utils import chain, config, misc

logging.basicConfig(level=logging.INFO)


def get_upper_lower(contract_address: str) -> Tuple[int, int]:
    """Get the upper and lower bound of the NFTs in a collection (on-chain).

    :param contract_address: Contract address of the collection
    :raises error: If on-chain fetching fails
    :return: A tuple with the lower and upper bound token id
    """
    try:
        abi = chain.get_contract_abi(address=contract_address)
        abi, contract = chain.get_contract(address=contract_address, abi=abi)

        lower_id = chain.get_lower_token_id(
            contract=contract, uri_func="tokenURI", abi=abi
        )

        total_supply_func = chain.get_contract_function(
            contract=contract, func_name="totalSupply", abi=abi
        )
        max_supply = total_supply_func().call()
        upper_id = max_supply + lower_id - 1
        logging.info(f"Lower ID of NFT collection: {lower_id}")
        logging.info(f"Upper ID of NFT collection: {upper_id}")
        logging.info(f"Max supply: {max_supply}")

        return lower_id, upper_id

    except Exception as error:
        logging.error("Error while trying to get the lower/upper IDs")
        logging.error(error)
        raise error


def is_nft_suspicious(nft_url: str, session: requests.Session) -> Optional[Dict]:
    """Download and parse the NFT page to check if it is flagged as suspicious

    :param nft_url: URL of the NFT page
    :param session: A requests.Session object
    :return: A dict with relevant information about the NFT and whether it is suspicious or not
    """
    logging.debug(f"Scraping NFT with link: {nft_url}")

    try:
        res = session.get(nft_url)
    except requests.exceptions.ChunkedEncodingError as error:
        logging.error(f"Error while trying to scrape {nft_url}")
        logging.error(error)
        return is_nft_suspicious(nft_url, session)

    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        collection_name = soup.find(class_="item--collection-detail").text
        owner = soup.find(class_="AccountLink--ellipsis-overflow").text.replace(
            "Owned by\xa0", ""
        )

        is_suspicious = res.text.find("Reported for suspicious") > 0
        nft_data = {
            "collection": args.contract,
            "collection_name": collection_name,
            "blockchain": "ethereum",
            "url": nft_url,
            "owner": owner,
            "is_suspicious": is_suspicious,
        }

        if is_suspicious:
            logging.info(f"Found suspicious NFT of URL {nft_url}")

        return nft_data
    elif res.status_code == 404:
        logging.info("NFT not found. Probably reached the end of a collection")
        return None
    else:
        logging.error(f"Error while trying to scrape NFT with link {nft_url}")
        logging.error(res.text)
        return None


def list_collection_nfts_urls(
    contract_address: str, lower_id: int, upper_id: int
) -> List[str]:
    """List all OpenSea URLs for the NFTs in a collection

    :param contract_address: Contract address of the collection
    :param lower_id: Lower bound token id
    :param upper_id: Upper bound token id
    :return: list of the OpenSea URLs of NFTs
    """
    nft_urls = []
    for i in range(lower_id, upper_id + 1):
        nft_urls.append(f"https://opensea.io/assets/ethereum/{contract_address}/{i}")
    return nft_urls


def main(
    contract_address: str, total_retries: int, backoff_factor: int, batch_size: int
) -> None:
    """Main function to scrape all NFTs in a collection and check if they are suspicious

    :param contract_address: Contract address of the collection
    :param total_retries: Total number of retries to allow.
    :param backoff_factor: A backoff factor to apply between attempts after the second try.
    :param batch_size: Batch size of NFT URLs to be processed
    """
    session = misc.mount_session(
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        total_retries=total_retries,
        backoff_factor=backoff_factor,
        raise_on_status=False,
        user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
    )

    lower_id, upper_id = get_upper_lower(contract_address)

    collection_nfts_urls = list_collection_nfts_urls(
        contract_address=contract_address, lower_id=lower_id, upper_id=upper_id
    )

    logging.info(f"Collection contains {len(collection_nfts_urls)} NFTs")

    collection_cache = load_scrape_cache(contract_address)
    logging.info(f"Found {len(collection_cache)} NFTs in collection cache")

    for index, nft in collection_cache.iterrows():
        if nft["url"] in collection_nfts_urls:
            logging.debug(f"NFT to be scraped already in cache. Skipping {nft['url']}")
            collection_nfts_urls.remove(nft["url"])
    logging.info(f"Scraping a list of {len(collection_nfts_urls)} NFTs")

    nft_urls_batches = [
        collection_nfts_urls[i : i + batch_size]
        for i in range(0, len(collection_nfts_urls), batch_size)
    ]
    for index, url_batch in enumerate(nft_urls_batches):
        logging.info(f"Scraped {index * batch_size} NFT URLs so far")

        batch = [(url, session) for url in list(url_batch)]

        with multiprocessing.Pool(multiprocessing.cpu_count() - 1) as p:
            results = p.starmap(is_nft_suspicious, batch)
            results = list(filter(None, results))
            if results == []:
                print(f"Reached a batch of NFTs not found. Exiting...")
                return

            df = pd.DataFrame(results)
            df.to_csv(
                f"{config.SUSPICIOUS_NFTS_FOLDER}/{contract_address}.csv",
                mode="a",
                header=False,
                index=False,
            )


def load_scrape_cache(contract_address: str) -> pd.DataFrame:
    """Loads cache of previously scraped collections, based on CSV files saved.

    :param contract_address: Contract address of the collection
    :return: Either a DataFrame with the scraped NFTs or an empty DataFrame if no cache is found
    """
    cache_file = f"{config.SUSPICIOUS_NFTS_FOLDER}/{contract_address}.csv"
    try:
        df = pd.read_csv(cache_file)
        return df
    except FileNotFoundError:
        logging.info("New collection to scrape. No cache detected.")
        logging.debug("Creating CSV with header for new collection to scrape")
        df = pd.DataFrame(
            columns=[
                "collection",
                "collection_name",
                "blockchain",
                "url",
                "owner",
                "is_suspicious",
            ]
        )
        df.to_csv(cache_file, index=False)
        return pd.DataFrame()


def _cli_parser() -> argparse.ArgumentParser:
    """
    Create the command line argument parser
    """
    parser = argparse.ArgumentParser(
        description="CLI for scraping NFTs flagged as suspicious on OpenSea."
    )

    parser.add_argument(
        "-c",
        "--contract",
        help="Collection contract address",
        required=True,
    )
    parser.add_argument(
        "-r",
        "--retries",
        help="Number of retry attempts",
        required=False,
        default=3,
    )
    parser.add_argument(
        "--backoff",
        help="Retries backoff parameter for failed requests",
        required=False,
        default=3,
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        help="Batch size of NFT URLs to be processed",
        required=False,
        default=50,
    )

    return parser


if __name__ == "__main__":

    args = _cli_parser().parse_args()

    main(
        contract_address=args.contract,
        total_retries=args.retries,
        backoff_factor=args.backoff,
        batch_size=args.batch_size,
    )
