# See https://github.com/convex-labs/honestnft-shenanigans/issues/86 for more details
# Given a collection of NFTs on OpenSea, detect suspicious NFTs
from argparse import ArgumentParser
import logging
import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)

parser = ArgumentParser()
parser.add_argument(
    "-c",
    "--collection",
    dest="collection_address",
    help="Address of the NFT collection",
    metavar="COLLECTION",
    required=True,
)

args = parser.parse_args()

COLLECTION_CSV_PATH = f"suspicious_{args.collection_address}.csv"


def is_nft_suspicious(nft_url):
    logging.debug(f"Scraping NFT with link: {nft_url}")
    scraper = cloudscraper.create_scraper()
    res = scraper.get(nft_url)

    if res.status_code == 429:  # Rate limited by OpenSea
        res = scraper.get(nft_url)
        logging.error(f"Hitting rate limits")
    if res.status_code == 404:  # NFT not found
        logging.info("NFT not found. Probably reached the end of a collection")
        return None, None
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        collection_name = soup.find(class_="item--collection-detail").text
        owner = soup.find(class_="AccountLink--ellipsis-overflow").text.replace(
            "Owned by\xa0", ""
        )
        data = {
            "collection": args.collection_address,
            "collection_name": collection_name,
            "blockchain": "ethereum",
            "url": nft_url,
            "owner": owner,
        }
        if res.text.find("Reported for suspicious") > 0:
            logging.info(
                f"Found suspicious NFT of URL {nft_url} in collection of address {args.collection_address}"
            )
            return True, data
        else:
            return False, data


OPENSEA_BASE_URL = (
    "https://opensea.io/assets/ethereum/"  # TODO adjust for other blockchains
)


def list_collection_nfts_urls(collection_address):
    """List all OpenSea URLs of NFTs in a collection

    Args:
        collection_address (string): NFT collection address

    Returns:
        array: list of the OpenSea URLs of NFTs
    """
    # ! This is just a mock function. It is to be replaced with a call to the OpenSea API
    nft_urls = []
    for i in range(9999, 10005):
        nft_urls.append(f"{OPENSEA_BASE_URL}{collection_address}/{i}")
    return nft_urls


def scrape_all_collection_suspicious_nfts(collection_address):
    collection_nfts_urls = list_collection_nfts_urls(collection_address)
    logging.info(f"Collection contains {len(collection_nfts_urls)} NFTs")
    collection_cache = load_scrape_cache(collection_nfts_urls)
    logging.info(f"Found {len(collection_cache)} NFTs in collection cache")
    # TODO removed scraped URLs from the list to be scraped
    for index, nft in collection_cache.iterrows():
        if (
            nft["url"] in collection_nfts_urls
        ):  # TODO add an expiry rule, depending on date of last scraped
            logging.info(f"NFT to be scraped already in cache. Skipping {nft['url']}")
            collection_nfts_urls.remove(nft["url"])
    logging.info(f"Scraping a list of {len(collection_nfts_urls)} NFTs")
    nfts = []
    for url in collection_nfts_urls:
        is_suspicious, result = is_nft_suspicious(url)
        if is_suspicious is None:  # ! To detect end of collection. To be removed.
            break
        result["is_suspicious"] = is_suspicious
        nfts.append(result)
    df = pd.DataFrame(nfts)
    df.to_csv(COLLECTION_CSV_PATH)
    logging.info(f"Stopped scraping. Reached end of the collection")


def load_scrape_cache(collection_address):
    """Loads cache of previously scraped collections, based on CSV files saved.

    Args:
        collection_address (string): Blockchain address of the NFT collection
    """
    try:
        df = pd.read_csv(COLLECTION_CSV_PATH)
        return df
    except FileNotFoundError:
        logging.info("New collection to scrape. No cache detected.")
        return pd.DataFrame()


scrape_all_collection_suspicious_nfts(args.collection_address)
