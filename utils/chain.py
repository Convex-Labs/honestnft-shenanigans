import json
import re
import sys
import time

import requests
from multicall import Call, Multicall
from web3 import Web3
from web3.exceptions import ContractLogicError

import utils.config as config
import utils.ipfs as ipfs


def get_contract_abi(address, blockchain="ethereum"):
    if blockchain == "arbitrum":
        abi_endpoint = config.ARBITRUM_ABI_ENDPOINT
        endpoint = config.ARBITRUM_ENDPOINT
    elif blockchain == "avalanche":
        abi_endpoint = config.AVALANCHE_ABI_ENDPOINT
        endpoint = config.AVALANCHE_ENDPOINT
    elif blockchain == "ethereum":
        abi_endpoint = config.ABI_ENDPOINT
        endpoint = config.ENDPOINT
    elif blockchain == "fantom":
        abi_endpoint = config.FANTOM_ABI_ENDPOINT
        endpoint = config.FANTOM_ENDPOINT
    elif blockchain == "optimism":
        abi_endpoint = config.OPTIMISM_ABI_ENDPOINT
        endpoint = config.OPTIMISM_ENDPOINT
    elif blockchain == "polygon":
        abi_endpoint = config.POLYGON_ABI_ENDPOINT
        endpoint = config.POLYGON_ENDPOINT
    else:
        raise ValueError(f"Blockchain {blockchain} not supported")

    # Get contract ABI
    abi_url = f"{abi_endpoint}{address}"
    response = requests.get(abi_url)
    try:
        abi = json.loads(response.json()["result"])
        return abi
    except Exception as err:
        print(f"Failed to get contract ABI from Etherscan: {err}")
        print("Falling back to direct ABI checking")
        if endpoint != "":
            # We can check the ABI of non-verified Etherscan contracts
            # if they support ERC165 (which most of them do)
            erc165_abi = [
                {
                    "inputs": [
                        {
                            "internalType": "bytes4",
                            "name": "interfaceId",
                            "type": "bytes4",
                        }
                    ],
                    "name": "supportsInterface",
                    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                    "stateMutability": "view",
                    "type": "function",
                }
            ]

            w3 = Web3(Web3.HTTPProvider(endpoint))
            contract = w3.eth.contract(Web3.toChecksumAddress(address), abi=erc165_abi)

            # Array of contract methods that were verified via ERC165
            contract_abi = []

            # List of common ERC721 methods to check
            common_abis = {}
            # ERC721 metadata interface id
            common_abis["0x5b5e139f"] = [
                {
                    "inputs": [],
                    "name": "name",
                    "outputs": [
                        {"internalType": "string", "name": "", "type": "string"}
                    ],
                    "stateMutability": "view",
                    "type": "function",
                },
                {
                    "inputs": [
                        {
                            "internalType": "uint256",
                            "name": "tokenId",
                            "type": "uint256",
                        }
                    ],
                    "name": "tokenURI",
                    "outputs": [
                        {"internalType": "string", "name": "", "type": "string"}
                    ],
                    "stateMutability": "view",
                    "type": "function",
                },
            ]
            # ERC721 enumerable interface id
            common_abis["0x780e9d63"] = [
                {
                    "inputs": [],
                    "name": "totalSupply",
                    "outputs": [
                        {"internalType": "uint256", "name": "", "type": "uint256"}
                    ],
                    "stateMutability": "view",
                    "type": "function",
                }
            ]

            for selector, abi in common_abis.items():
                try:
                    supports_abi = contract.functions.supportsInterface(selector).call()
                    if supports_abi:
                        contract_abi += abi
                except Exception as err:
                    print(f"Could not check selector {selector}")

            if len(contract_abi) > 0:
                return contract_abi

        raise Exception(
            f"Failed to get contract ABI.\nURL: {abi_url}\nResponse: {response.json()}"
        )


def get_contract(address, abi, blockchain="ethereum"):
    if blockchain == "arbitrum":
        endpoint = config.ARBITRUM_ENDPOINT
    elif blockchain == "avalanche":
        endpoint = config.AVALANCHE_ENDPOINT
    elif blockchain == "ethereum":
        endpoint = config.ENDPOINT
    elif blockchain == "fantom":
        endpoint = config.FANTOM_ENDPOINT
    elif blockchain == "optimism":
        endpoint = config.OPTIMISM_ENDPOINT
    elif blockchain == "polygon":
        endpoint = config.POLYGON_ENDPOINT
    else:
        raise ValueError(f"Blockchain {blockchain} not supported")

    # Connect to web3
    if endpoint == "":
        print(
            "\nMust enter a Web3 provider. Open this file and set the ENDPOINT and IPFS_GATEWAY constants. See: https://ipfs.github.io/public-gateway-checker/\n"
        )
        print("Optional: Use -web3_provider as a command line argument")
        sys.exit()

    w3 = Web3(Web3.HTTPProvider(endpoint))

    # Check if abi contains the tokenURI function
    contract_functions = [func["name"] for func in abi if "name" in func]
    # Get contract checksum address
    contract_checksum_address = Web3.toChecksumAddress(address)

    # Check if the contract is a proxy contract
    # Current heuristic: contract functions contains "implementation"
    if [
        func
        for func in contract_functions
        if re.search("implementation", func, re.IGNORECASE)
    ]:
        # Fetch address for the implementation contract
        impl_contract = w3.toHex(
            w3.eth.get_storage_at(contract_checksum_address, config.IMPLEMENTATION_SLOT)
        )

        # Strip the padded zeros from the implementation contract address
        impl_address = "0x" + impl_contract[-40:]
        print(
            f"Contract is a proxy contract. Using implementation address: {impl_address}"
        )

        # Sleep to respect etherscan API limit
        time.sleep(5)

        # Get the implementation contract ABI
        impl_abi = get_contract_abi(address=impl_address, blockchain=blockchain)

        # Return the original address and the proxy ABI
        return get_contract(address, abi=impl_abi, blockchain=blockchain)

    # Build the Ethereum contract object
    collection_contract = w3.eth.contract(contract_checksum_address, abi=abi)

    # Return the contract ABI and Ethereum contract object
    return abi, collection_contract


def get_contract_function(contract, func_name, abi):
    if func_name in dir(contract.functions):
        # The function name given is a valid function in the ABI, so return that function
        return getattr(contract.functions, func_name)
    else:
        # The function name provided is not in the contract ABI, so throw an error
        func_names = [f["name"] for f in abi if "name" in f]
        raise ValueError(
            f"{func_name} is not in the contract ABI. Inspect the following function names "
            f"for candidates and pass to the command line arguments: {func_names}"
        )


def get_token_uri_from_contract(contract, token_id, uri_func, abi):
    # Fetch URI from contract
    uri_contract_func = get_contract_function(contract, uri_func, abi)

    try:
        uri = uri_contract_func(token_id).call()
        uri = ipfs.format_ipfs_uri(uri)
        return uri
    except ContractLogicError as err:
        raise Exception(err)


def get_token_uri_from_contract_batch(
    contract, token_ids, function_signature, abi, blockchain="ethereum"
):
    if blockchain == "arbitrum":
        endpoint = config.ARBITRUM_ENDPOINT
    elif blockchain == "avalanche":
        endpoint = config.AVALANCHE_ENDPOINT
    elif blockchain == "ethereum":
        endpoint = config.ENDPOINT
    elif blockchain == "fantom":
        endpoint = config.FANTOM_ENDPOINT
    elif blockchain == "optimism":
        endpoint = config.OPTIMISM_ENDPOINT
    elif blockchain == "polygon":
        endpoint = config.POLYGON_ENDPOINT
    else:
        raise ValueError(f"Blockchain {blockchain} not supported")

    if len(token_ids) > 0:
        if endpoint == "":
            print(
                "You must enter a Web3 provider. This is currently not a command line option. You must open this file and assign a valid provider to the ENDPOINT and IPFS_GATEWAY constants. See: https://ipfs.github.io/public-gateway-checker/"
            )
            sys.exit()

        w3 = Web3(Web3.HTTPProvider(endpoint))

        calls = []
        for token_id in token_ids:
            call = Call(
                target=contract.address,
                function=[function_signature, token_id],
                returns=[[token_id, ipfs.format_ipfs_uri]],
            )
            calls.append(call)
        multi = Multicall(calls, _w3=w3)
        return multi()

    else:
        return {}


def get_lower_token_id(contract, uri_func, abi):
    # Initiate parameters
    lower_token_id = None

    # Search over possible lower bound ids
    for token_id in [0, 1]:
        try:
            # Fetch the metadata url from the contract
            uri = get_token_uri_from_contract(contract, token_id, uri_func, abi)
            print(f"Metadata for lower bound token id is at: {uri}")
            lower_token_id = token_id
            break
        except Exception as err:
            # Catch exception where token URI function fails because the token id is invalid
            print(err)
            pass

    # Raise exception if method fails to find the metadata url
    if lower_token_id is None:
        raise Exception("Unable to get the metadata url.")

    # Return lower id
    return lower_token_id


def get_base_uri(contract, abi):
    uri_contract_func = get_contract_function(contract, "baseURI", abi)

    try:
        uri = uri_contract_func().call()
        return uri
    except ContractLogicError as err:
        raise Exception(err)


def get_function_signature(func_name, abi):
    """
    Given a function name and an ABI, return the function signature
    e.g. get_function_signature("tokenURI", abi) => "tokenURI(uint256)(string)"

    :param func_name:
    :type func_name: str
    :param abi:
    :type abi: list
    :return: function signature
    :rtype: str
    """
    try:
        filtered = list(
            filter(
                lambda d: d["name"] == func_name if d["type"] == "function" else None,
                abi,
            )
        )[0]
    except IndexError:
        raise ValueError(f"{func_name} is not a valid function name")
    input_types = [obj["type"] for obj in filtered["inputs"]]
    output_types = [obj["type"] for obj in filtered["outputs"]]
    return f"{func_name}({','.join(input_types)})({','.join(output_types)})"
