============
Contributing
============


Welcome, and thank you for considering contributing to honestnft-shenanigans. 
We encourage you to help out by raising issues, improving documentation, fixing 
bugs, or adding new features.

If you're interested in contributing please start by reading this document. If
you have any questions at all, or don't know where to start, please reach out to
us on Discord_.

Contributing Code
=================
To contribute bug fixes or features to honestnft-shenanigans:

1. Communicate your intent.
2. Make your changes.
3. Test your changes.
4. Update documentation and examples where appropriate.
5. Open a Pull Request (PR).

Communicating your intent lets the honestnft-shenanigans maintainers know that 
you intend to contribute, and how. This sets you up for success - you can avoid 
duplicating an effort that may already be underway, adding a feature that may 
be rejected, or heading down a path that you would be steered away from at review 
time. The best way to communicate your intent is via a detailed GitHub issue. 
Take a look first to see if there's already an issue relating to the thing you'd 
like to contribute. If there isn't, please raise a new one! Let us know what you'd 
like to work on, and why. The honestnft-shenanigans maintainers can't always triage 
new issues immediately, but we encourage you to bring them to our attention 
via Discord_.

Be sure to practice `good git commit hygiene`_ as you make your changes. All but
the smallest changes should be broken up into a few commits that tell a story.
Use your git commits to provide context for the folks who will review PR, and
the folks who will be spelunking the codebase in the months and years to come. 
The honestnft-shenanigans project highly values readable, Pythonic Python code. 

Once your change is written, tested, and documented the final step is to have it
reviewed! You'll be presented with a template and a small checklist when you
open a PR. Please read the template and fill out the checklist. Please make all
requested changes in subsequent commits. This allows your reviewers to see what
has changed as you address their comments. Be mindful of your commit history as
you do this - avoid commit messages like "Address review feedback" if possible.
If doing so is difficult a good alternative is to rewrite your commit history to
clean them up after your PR is approved but before it is merged.

In summary, please:

* Discuss your change in a GitHub issue before you start.
* Use your Git commit messages to communicate your intent to your reviewers.
* Add or update tests for all changes.
* Update all relevant documentation.
* Don't force push to address review feedback. Your commits should tell a story.
* If necessary, tidy up your git commit history once your PR is approved.

Pull Requests
=============
Please follow these steps and suggestions to have your contribution considered by the maintainers.

* Enable the checkbox to allow maintainer edits so the branch can be updated for a merge. [#f1]_ 
* Make sure your branch is up to date with master.
* After you submit your pull request, verify that all status checks are passing. [#f2]_
  * Try to resolve the failures by reading the detailed report.
  * A new status check will automatically start when you push your changes.

Workflow for developers
-----------------------
This repo uses automatic status checks to ensure all code is formatted in a uniform way. 
To reduce friction and limit extra work, we use `pre-commit hooks`_ to run checks and/or format your code with Black_. 
In short, for each commit you make, pre-commit will be triggered and will run the following checks:
* Trim Trailing Whitespace
* Fix End of Files
* Format your code with Black and automatically fix any issues.

General Requirements
--------------------
1. Install developer dependencies :code:`pip install -r requirements-dev.txt`
2. Prepare your local environment with the command :code:`pre-commit install`
3. Run a test to see if it works as expected: :code:`pre-commit run --all-files`


.. raw:: html

   <details>
   <summary>The output will be different depending on the state of the repo you are running it in.</summary>


◦ e.g. A repo with all files already formatted with Black: ::

    Trim Trailing Whitespace.................................................Passed
    Fix End of Files.........................................................Passed
    black....................................................................Passed
    black-jupyter............................................................Passed

◦ e.g. A test repo without any python files: ::

    Trim Trailing Whitespace.............................(no files to check)Skipped
    Fix End of Files.....................................(no files to check)Skipped
    black................................................(no files to check)Skipped
    black-jupyter........................................(no files to check)Skipped

◦ e.g. A test repo with an unformatted file: :: 

    Trim Trailing Whitespace.................................................Passed
    Fix End of Files.........................................................Passed
    black....................................................................Failed
    - hook id: black
    - files were modified by this hook

    reformatted rarity.py
    All done! ✨ 🍰 ✨
    1 file reformatted.

Now you only have to stage the changes before committing.


.. raw:: html

    </details>
    <br>


Using Black in your IDE
-----------------------

Visual Studio Code
^^^^^^^^^^^^^^^^^^
At the root of your cloned repo, create a new file named `.vscode/settings.json`

.. code-block:: json

    {
        "python.formatting.provider": "black"
    }   

PyCharm
^^^^^^^^
Setting up a working integration with Black is a bit more work, but still relatively easy. Just follow the instructions from the `Black docs`_.

--------

Thank you for reading through our contributing guide! We appreciate you taking
the time to ensure your contributions are high quality and easy for our
community to review and accept. Please don't hesitate to reach out to
us on Discord_ if you have any questions about contributing!





.. _Discord: https://discord.gg/gJFw7R8bys
.. _good git commit hygiene: https://www.futurelearn.com/info/blog/telling-stories-with-your-git-history
.. _Black docs: https://black.readthedocs.io/en/stable/integrations/editors.html
.. _pre-commit hooks: https://pre-commit.com/
.. _Black: https://black.readthedocs.io/en/stable/
.. [#f1] https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork
.. [#f2] https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks