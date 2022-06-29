Frequently Asked Questions
==========================

ModuleNotFoundError
-------------------
**Q:** *I keep getting this error "ModuleNotFoundError: No module named 'is_ipfs'" when running one of the scripts*

**A:** This means that "Python" can't find one of the modules that is used in the script. There can be multiple causes...
If you didn't modify the scripts it's most likely due to a failed or incomplete install. From the root of the project directory (where you can find the setup.py), execute the command :code:`python3 -m pip install --editable .` from the terminal.
This should download all the missing dependencies.


I keep getting this error "ModuleNotFoundError: No module named 'is_ipfs'" when running one of the scripts
----------------------------------------------------------------------------------------------------------
This means that "Python" can't find one of the modules that is used in the script. There can be multiple causes...
If you didn't modify the scripts it's most likely due to a failed or incomplete install. From the root of the project directory (where you can find the setup.py), execute the command :code:`python3 -m pip install --editable .` from the terminal.
This should download all the missing dependencies.

