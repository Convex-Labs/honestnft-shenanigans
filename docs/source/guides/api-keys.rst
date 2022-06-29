API keys & Providers
====================

`honestnft-shenanigans` aggregates data from multiple sources and most sources require an API key or some extra configuration.

Blockchain RPC endpoint (web3 providers)
----------------------------------------

You will need a web3 provider for each blockchain you want to use. Most providers have a free tier that should be enough for our use-case.
Some examples are:

* https://www.alchemy.com/
* https://infura.io/
* https://moralis.io (speedynodes)


IPFS gateway
------------

The default gateway is set to `https://dweb.link/ipfs/`, but can be changed if necessary. 
A list of public gateways can be found on https://ipfs.github.io/public-gateway-checker/

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
A free key can be requested at https://docs.opensea.io/reference/request-an-api-key

Moralis
^^^^^^^
A free key can be registered at https://moralis.io