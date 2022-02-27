import os
import warnings
import papermill as pm

from utils import config

COLLECTION_NAME = "Quaks"
CONTRACT = "0x07bbdaf30e89ea3ecf6cadc80d6e7c4b0843c729"
OUTPUT_FOLDER = "OUT"

if not os.path.exists(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)

# Ignore papermill warnings when we output to /dev/null
warnings.filterwarnings(
    "ignore",
    module="papermill",
    message="the file is not specified with any extension : null",
)

# Generate rarity map
pm.execute_notebook(
    f"{config.ROOT_DIR}/fair_drop/rarity_map.ipynb",
    f"{config.ROOT_DIR}/{OUTPUT_FOLDER}/rarity_map-output.ipynb",
    parameters=dict(FILE=COLLECTION_NAME),
)

# Download minting data from Moralis
pm.execute_notebook(
    f"{config.ROOT_DIR}/fair_drop/find_minting_data_from_moralis.ipynb",
    "/dev/null",
    parameters=dict(COLLECTION_NAME=COLLECTION_NAME, CONTRACT=CONTRACT, CHAIN="eth"),
)

# Generate KS-test
pm.execute_notebook(
    f"{config.ROOT_DIR}/fair_drop/ks_test.ipynb",
    f"{OUTPUT_FOLDER}/ks_test-output.ipynb",
    parameters=dict(COLLECTION=COLLECTION_NAME),
)
