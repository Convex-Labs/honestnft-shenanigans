import os

from dotenv import dotenv_values

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = dotenv_values(f"{ROOT_DIR}/.env")


###
# ABI endpoints
###
ABI_ENDPOINT = "https://api.etherscan.io/api?module=contract&action=getabi&address="
ARBITRUM_ABI_ENDPOINT = (
    "https://api.arbiscan.io/api?module=contract&action=getabi&address="
)
AVALANCHE_ABI_ENDPOINT = (
    "https://api.snowtrace.io/api?module=contract&action=getabi&address="
)
BINANCE_SCAN_ABI_ENDPOINT = (
    "https://api.bscscan.com/api?module=contract&action=getabi&address="
)
FANTOM_ABI_ENDPOINT = (
    "https://api.ftmscan.com/api?module=contract&action=getabi&address="
)
OPTIMISM_ABI_ENDPOINT = (
    "https://api-optimistic.etherscan.io/api?module=contract&action=getabi&address="
)
POLYGON_ABI_ENDPOINT = (
    "https://api.polygonscan.com/api?module=contract&action=getabi&address="
)

###
# web3 providers
###
ENDPOINT = config.get("web3_provider")
ARBITRUM_ENDPOINT = config.get("arbitrum_web3_provider")
AVALANCHE_ENDPOINT = config.get("avalanche_web3_provider")
BINANCE_ENDPOINT = config.get("binance_web3_provider")
FANTOM_ENDPOINT = config.get("fantom_web3_provider")
OPTIMISM_ENDPOINT = config.get("optimism_web3_provider")
POLYGON_ENDPOINT = config.get("polygon_web3_provider")

###
# Project folders
###
ROOT_DATA_FOLDER = f"{ROOT_DIR}/data"
ATTRIBUTES_FOLDER = f"{ROOT_DATA_FOLDER}/raw_attributes"
RARITY_FOLDER = f"{ROOT_DATA_FOLDER}/rarity_data"
MINTING_FOLDER = f"{ROOT_DATA_FOLDER}/minting_data"
FIGURES_FOLDER = f"{ROOT_DATA_FOLDER}/figures"
FIRST_FLIP_PROFITS_FOLDER = f"{ROOT_DATA_FOLDER}/first_flip_profits"
FIRST_FLIP_REVENUE_FOLDER = f"{ROOT_DATA_FOLDER}/first_flip_revenue"
PRE_REVEAL_BIDS_FOLDER = f"{ROOT_DATA_FOLDER}/pre-reveal_bids"
PRE_REVEAL_SALES_FOLDER = f"{ROOT_DATA_FOLDER}/pre-reveal_sales"
SALES_DATA_FOLDER = f"{ROOT_DATA_FOLDER}/sales_data"
GRIFTERS_DATA_FOLDER = f"{ROOT_DATA_FOLDER}/grifters"

###
# Misc
###
IMPLEMENTATION_SLOT = (
    "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
)
IPFS_GATEWAY = config.get("ipfs_gateway")

###
# API keys
###
OPENSEA_API_KEY = config.get("opensea_api_key")
MORALIS_API_KEY = config.get("moralis_api_key")
THE_INDEX_API_KEY = config.get("the_index_api_key")
