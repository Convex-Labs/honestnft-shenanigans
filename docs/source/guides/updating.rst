Updating
========

Regular update
--------------
If you installed `honestnft-shenanigans` like we advised in the :doc:`install instructions <install>`, updating can be done in a few commands.

1. Open the terminal and go to the base folder of the repo (where you can find the `setup.py`)
2. Download the latest changes from GitHub with :code:`git pull`
   If it was successful the output should be similar to: ::

    Updating xxxxxxx..yyyyyyy
    Fast-forward
    folder1/file.py              |  9 ++++++---
    folder2/test.py              |   6 +++++-
    folder1/file2.py             | 13 +++++++++++++
    3 files changed, 24 insertions(+), 4 deletions(-)


3. Next, re-install the latest changes with :code:`python3 -m pip install --editable .`


Common issues
-------------
Git complains about local changes: ::

    error: Your local changes to the following files would be overwritten by merge:
        folder1/file.py
    Please commit your changes or stash them before you merge.
    Aborting


The error message is self-explanatory. If you think you didn't modify the file (on purpose), 
you can restore the file with the command: :code:`git restore folder1/file.py` and then you can retry to download the latest changes.
If you did modify that file on purpose, you probably know what you're doing and can fix this on your own.

