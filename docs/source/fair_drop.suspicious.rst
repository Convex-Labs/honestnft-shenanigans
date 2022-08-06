fair_drop.suspicious
====================

This module can be used to scrape a NFT collection on OpenSea for tokens flagged as suspicious.
Scraped data is stored in `data/suspicious_nfts/`.

.. note::
   * We currently only support collections with incrementing IDs
   * Only Ethereum NFTs can be scraped

.. autoprogram:: fair_drop.suspicious:_cli_parser()
   :prog: suspicious.py
   :no_description:
   :custom_title: Command Line

------------

Internal functions
------------------
.. automodule:: fair_drop.suspicious
   :members:
   :undoc-members:
   :show-inheritance:
