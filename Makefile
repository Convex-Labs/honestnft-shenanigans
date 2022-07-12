help:
	@echo "build-docs - build documentation"
	@echo "view-docs - clean & rebuild HTML (only) and open in firefox"
	@echo "clean-build - remove build artifacts"

clean: clean-build 

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

build-docs:
	sphinx-apidoc --separate --module-first --templatedir=docs/source/_templates/apidoc --output-dir docs/source . "tests" "setup.py"
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

refresh-docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html	

view-docs: refresh-docs
	firefox docs/build/html/index.html
