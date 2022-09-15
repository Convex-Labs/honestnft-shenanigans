fair_drop.suspicious
====================

.. note::
   * We currently only support collections with incrementing IDs
   * Only Ethereum NFTs can be scraped
   * A CSS selector is now required to find the correct DOM element


This module can be used to scrape a NFT collection on OpenSea for tokens flagged as suspicious.
The scraped data is stored in `data/suspicious_nfts/` as a JSON file with extra metadata.
The scraped_on field is a UNIX timestamp (epoch) for when the file was created.

.. code-block:: json

   {
    "contract": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
    "name": "Bored Ape Yacht Club",
    "scraped_on": 1659948199,
    "data": [
        {
            "token_id": 0,
            "url": "https://opensea.io/assets/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/0",
            "is_suspicious": false
        },
        {
            "token_id": 1,
            "url": "https://opensea.io/assets/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/1",
            "is_suspicious": false
        },
        {
            "token_id": 2,
            "url": "https://opensea.io/assets/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/2",
            "is_suspicious": false
        }
      ]
   }

Example
-------
To scrape the BAYC collection from OpenSea, you only need to supply the contract address and the CSS selector to find the "suspicious flag". All other CLI arguments are optional.

.. code-block:: shell

   $ python3 fair_drop/suspicious.py --contract 0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d --selector "i.sc-e8292ad1-0.gZavKY.material-icons"


Command Line
------------
.. autoprogram:: fair_drop.suspicious:_cli_parser()
   :prog: suspicious.py
   :no_description:
   :no_title: 

------------

Internal functions
------------------
.. automodule:: fair_drop.suspicious
   :members:
   :undoc-members:
   :show-inheritance:
