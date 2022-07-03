# See https://github.com/convex-labs/honestnft-shenanigans/issues/86 for more details
# Given a collection of NFTs on OpenSea, detect suspicious NFTs
from argparse import ArgumentParser
import logging
import cloudscraper


logging.basicConfig(level=logging.INFO)

parser = ArgumentParser()
parser.add_argument(
    "-c",
    "--collection",
    dest="collection_address",
    help="Address of the NFT collection",
    metavar="COLLECTION",
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
        if res.text.find("Reported for suspicious") > 0:
            logging.info(
                f"Found suspicious NFT of URL {nft_url} in collection of address {args.collection_address}"
            )
            return True
        else:
            return False
