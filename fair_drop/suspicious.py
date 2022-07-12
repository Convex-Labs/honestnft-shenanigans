# See https://github.com/convex-labs/honestnft-shenanigans/issues/86 for more details
# Given a collection of NFTs on OpenSea, detect suspicious NFTs
from argparse import ArgumentParser
import logging
import cloudscraper
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


def is_nft_suspicious(nft_url):
    logging.info(f"Scraping NFT with link: {nft_url}")
    scraper = cloudscraper.create_scraper()
    res = scraper.get(nft_url)

    if res.status_code == 429:  # Rate limited by OpenSea
        res = scraper.get(nft_url)
        logging.error(f"Hitting rate limits")
    if res.status_code == 404:  # NFT not found
        logging.info("NFT not found. Probably reached the end of a collection")
        return None
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


results = {}
OPENSEA_BASE_URL = (
    "https://opensea.io/assets/ethereum/"  # TODO adjust for other blockchains
)


def scrape_all_collection_suspicious_nfts(collection_address):
    i = 1
    result = is_nft_suspicious(f"{OPENSEA_BASE_URL}{collection_address}/{i}")
    nfts = []
    while result is not None:
        results[i] = result
        i += 1
        is_suspicious, result = is_nft_suspicious(
            f"{OPENSEA_BASE_URL}{collection_address}/{i}"
        )
        result["is_suspicious"] = is_suspicious
        nfts.append(result)
    logging.info(f"Stopped scraping at NFT of ID {i}")


scrape_all_collection_suspicious_nfts(args.collection_address)
