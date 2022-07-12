
metadata.solana_pull
====================

solana_pull is a nodejs script to download metadata for Solana NFT's.

Installation
------------

.. code-block:: bash
   
      yarn install


Usage
-----

Args
^^^^
- `contract` `Solana Explorer <https://explorer.solana.com/address/CwXveCXpWmwUdVLKbQg2t6vhrj6pNWvsyfnFvqcPCxsP>`_ > `Update Authority`
- `collection` Collection name

Example
^^^^^^^

.. code-block:: bash
      
      node solana-pull.js -contract F5FKqzjucNDYymjHLxMR2uBT43QmaqBAMJwjwkvRRw4A -collection SolPunks
