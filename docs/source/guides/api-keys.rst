API keys & Providers
====================

`honestnft-shenanigans` aggregates data from multiple sources and most sources require an API key or some extra configuration.

Blockchain RPC endpoint (web3 providers)
----------------------------------------

.. note::
  We added public web3 providers to the .env-example so you can get started right away. If you run into issues or rate-limiting, 
  you might need to set up a private endpoint.

You will need a web3 provider for each blockchain you want to use. Most providers have a free tier that should be enough for our use-case.
Some examples are:

* Alchemy_
* Infura_


IPFS gateway
------------

The default gateway is set to `https://dweb.link/ipfs/`, but can be changed if necessary. 
A list of public gateways can be found on the `IPFS Public Gateway Checker <https://ipfs.github.io/public-gateway-checker/>`_.

.. note::
  When you click on one of the gateways, you might be redirected to a long URL. Please note that only the :code:`hostname + /ipfs/` part is necessary.  
  E.g. ::

    Correct: gateway.ipfs.io/ipfs/
    Wrong: gateway.ipfs.io/ipfs/bafybeifx7yeb55armcsxwwitkymga5xf53dxiarykms3ygqic223w5sk3m#x-ipfs-companion-no-redirect  
    

In some cases a private gateway can lead to faster downloads.


API keys
--------

OpenSea
^^^^^^^
A free key can be requested at `OpenSea <https://docs.opensea.io/reference/request-an-api-key>`_.

Moralis
^^^^^^^
A free key can be registered at Moralis_.

.. _Alchemy: https://www.alchemy.com
.. _Moralis: https://moralis.io
.. _Infura: https://infura.io/
.. 