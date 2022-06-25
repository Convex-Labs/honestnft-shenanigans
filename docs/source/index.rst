Welcome to HonestNFT Shenanigan Scanning Tools's documentation!
========================================================================

Motivation
---------------
At `Convex Labs <https://www.convexlabs.xyz>`_, we're NFT fanatics. We believe 
that NFTs represent a revolution in the art and collectibles spaces. 
Unfortunately, as described in `Paradigm's Guide to Designing Effective NFT 
Launches <https://www.paradigm.xyz/2021/10/a-guide-to-designing-effective-nft-launches/>`_, the current systems being used for NFT launches are often unfair to 
average users. Hasu and Agnihotri describe several pitfalls which can give 
sophisticated users an edge and allow such users to extract value from both 
creators and other collectors.

We have developed and deployed tools for the purpose of gaining an advantage when 
buying NFTs and we aren't the only ones; we've been observing people using such 
tools for months and recently numerous paid services such as traitsniper.com 
have appeared. We've open sourced our tools, describing how we use them, and how 
to detect when someone else has used similar methods to gain an advantage in an 
NFT launch.
  
Continue reading about our motivation / background `here <https://medium.com/@convexlabs/a76143ef8ad8>`_.

  
Bug Bounty 
---------------
Our bug bounty program is an experimental and discretionary rewards program modeled after the Ethereum bug bounty program. We will give NFTs, Ether, or other prizes to participants who improve our codebase or find dishonest drops.
We are seeding our initial bug bounty pool with 100% of the profits we made trading NFTs with our code. We encourage others to donate to our bounty pool multisig.
 
Our Gnosis Safe Multisig: `0xa94a1B82B441DAA23890FF5eEb84a66D323Fd6c1 <https://etherscan.io/address/0xa94a1b82b441daa23890ff5eeb84a66d323fd6c1>`_

Read more about our rewards program `here <https://medium.com/@convexlabs/list/bounties-c0efbd75cf8c/>`_
  
Installation
---------------

**1. Prerequisites**

- python
- git

**2. Instructions**

1. Download the github repo: :code:`git clone https://github.com/Convex-Labs/honestnft-shenanigans.git`  
2. Change directory to the downloaded repo: :code:`cd honestnft-shenanigans`
3. Install the tools and requirements with: :code:`pip install --editable .`
4. Rename :code:`.env-example` to :code:`.env`
5. Add your personal API keys and web3 providers to :code:`.env`

**Note**: The repo takes a few minutes to install. We've provided a decent amount 
of test data so the repository is rather large.


Simple Tutorial
------------------------------
1. Download metadata with `pulling.py <https://github.com/Convex-Labs/honestnft-shenanigans/blob/master/metadata/pulling.py>`_
2. Generate rarity rank with `rarity.py https://github.com/Convex-Labs/honestnft-shenanigans/blob/master/metadata/rarity.py`_ (ranks are based off rarity.tools algorithm, which we reverse engineered)
3. Generate rarity map (scatterplot) with `rarity_map.ipynb <https://github.com/Convex-Labs/honestnft-shenanigans/blob/master/fair_drop/rarity_map.ipynb>`_
4. Pull minting data with `find_minting_data.ipynb <https://github.com/Convex-Labs/honestnft-shenanigans/blob/master/fair_drop/find_minting_data.ipynb>`_
5. Generate ks-test scores with `ks_test.ipynb <https://github.com/Convex-Labs/honestnft-shenanigans/blob/master/fair_drop/ks_test.ipynb>`_ (ignore ks-test results for drops with skewed rarity maps)
6. Tell us what you find! 



Video Tutorial
------------------------------
Tutorial: https://vimeo.com/638878051



.. API References
.. ------------------------------
.. Web3 Provider: https://www.alchemy.com/ (Recommended)

.. Basic IPFS Endpoints: https://ipfs.github.io/public-gateway-checker/
.. <details>
..   <summary>Note</summary>
  
..   When you click one the gateways, you might be redirected to a long URL. Please note that only the hostname + /ipfs/ part is necessary.  
..   E.g.  
  
..   ```
..   Correct: gateway.ipfs.io/ipfs/  
..   Wrong: gateway.ipfs.io/ipfs/bafybeifx7yeb55armcsxwwitkymga5xf53dxiarykms3ygqic223w5sk3m#x-ipfs-companion-no-redirect  
..   ```
  
..   </details>
.. Pinata IPFS Endpoints: https://www.pinata.cloud/ (IPFS_GATEWAY in pulling.py is 
.. set to a public endpoint; can pull faster w Pinata)

How metadata leaks 
------------------------------
`A Guide to Effectively Cheating NFT Launches (and detecting cheaters) <https://medium.com/@convexlabs/a-guide-to-effectively-cheating-nft-launches-and-detecting-cheaters-a76143ef8ad8>`_


Future Work Ideas
------------------------------

- Spikes in minting before rare tokens
- Median rarity in sliding windows of length N
- Unusually high amounts of "1 mint" buyers getting rare tokens (ie minting one token and getting one rare; ks-test isn't super sensitive to this)
- Rare items getting listed at the same time. It is very interesting if multiple addresses list super rare items at the same time. Maybe these addresses all belong to one person?
 


Support
---------------
For help, visit the `🔨#support channel <https://discord.gg/4aHvBBEq3p>`_ in our Discord.
 

Contributing 
---------------
Contributions, issues, feature requests or even suggestions are welcome! You can open an issue/PR or join us on `Discord <https://discord.gg/gJFw7R8bys>`_ to discuss your contribution. You can even earn a nice `bounty <bug-bounty>`_.

Don't forget to check out our `contributing guide <https://github.com/Convex-Labs/honestnft-shenanigans/blob/master/CONTRIBUTING.md>`_. 



.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
