# Suspicious NFTs

This script's goal is to scrape an NFT's page on OpenSea and determine whether or not it is marked as suspicious.

Here are example of suspicious NFTs, as of the date of writing:

- https://opensea.io/assets/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/71
- https://opensea.io/assets/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/1181
- https://opensea.io/assets/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/1207
- https://opensea.io/assets/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/1277

For now, the script is limited to:

- Collections on the Ethereum blockchain
- Collections that use auto-incrementing IDs for their NFTs

All of these limitations can be resolved if we either:

1. Get a function that lists all OpenSea URLs to NFTs of a collection
2. List the IDs of the NFTs and deduce the OpenSea URLs

Both of the above will have to, optionally, take into considerations ever-growing NFT collections such as ENS.

## Outliers

Some NFT collection use un-predictable IDs for their NFTs, and present challenges for this script:

- Extremly large and seemingly random IDs: [Mirandus](https://opensea.io/collection/mirandus) has IDs [281413517443616109284210800346072310874112](https://opensea.io/assets/ethereum/0xc36cf0cfcb5d905b8b513860db0cfe63f6cf9f5c/281413517443616109284210800346072310874112)
- IDs are prepended with a number: [Anticyclone](https://opensea.io/collection/anticyclone-by-william-mapan) has IDs such as [304000399](https://opensea.io/assets/ethereum/0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270/304000399) and [304000158](https://opensea.io/assets/ethereum/0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270/304000158)
- ENS

## Script options

Retries and Backoff: these are request retries parameters designed to make the script more resilient and handle rate-limiting from OpenSea
Batch size: the list of NFTs is trated in batches, distributed to 5 threads. Once these threads have scraped the batch, it is appended to the CSV

You can see more options using `python fair_drop/suspicious.py --help`

## Improvements

1. Suspicious or not, this data needs to go with: current and past owners, creator, past trades and orders, current price...
2. A user's OpenSea profile may be also marked as `compromised` e.g. https://opensea.io/JonnyUtah007