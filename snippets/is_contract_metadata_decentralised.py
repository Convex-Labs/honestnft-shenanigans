import os
import sys

from utils import chain, ipfs

contract_address = "0x60d9b4f9d85695274a5777537f204675082bd745"

abi = chain.get_contract_abi(address=contract_address)
abi, contract = chain.get_contract(address=contract_address, abi=abi)

try:
    base_uri = chain.get_base_uri(contract=contract, abi=abi)
    print(ipfs.is_valid_ipfs_uri(base_uri))
except Exception as err:
    print("Failed to get base URI")
    print("Trying to infer baseURI from tokenURI")
    for token_id in [0, 1]:
        try:
            # Fetch the metadata url from the contract
            uri = chain.get_token_uri_from_contract(contract, token_id, "tokenURI", abi)
            if ipfs.is_valid_ipfs_uri(uri):
                print("This file is hosted on IPFS")
            else:
                print("This file is not hosted on IPFS")
                print(uri)
            break
        except Exception as err:
            pass
