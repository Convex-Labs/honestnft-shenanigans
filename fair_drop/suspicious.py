# See https://github.com/convex-labs/honestnft-shenanigans/issues/86 for more details
# Given a collection of NFTs on OpenSea, detect suspicious NFTs
from argparse import ArgumentParser
import cloudscraper

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
    scraper = cloudscraper.create_scraper()
    res = scraper.get(nft_url)
    if res.status_code == 429:  # Rate limited by OpenSea
        res = scraper.get(nft_url)
    if res.status_code == 404:  # NFT not found
        return None
    if res.status_code == 200:
        return res.text.find("Reported for suspicious") > 0
