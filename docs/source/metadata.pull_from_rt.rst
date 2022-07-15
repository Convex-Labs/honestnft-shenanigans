
metadata.pull\_from\_rt
=======================

This module can be used to download NFT metadata and rarity data from rarity.tools.
Whereas most of our modules rely on the contract address, this one relies on the exact project name, as mentioned on the rarity.tools website.


.. code-block:: shell

   $ python3 metadata/pull_from_rt.py --collection cryptopunks


.. autoprogram:: metadata.pull_from_rt:_cli_parser()
   :prog: pull_from_rt.py
   :no_description:
   :custom_title: Command Line

------------

Internal functions
------------------
.. automodule:: metadata.pull_from_rt
   :members:
   :undoc-members:
   :show-inheritance:
