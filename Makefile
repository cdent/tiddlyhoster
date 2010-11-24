# Simple Makefile for some common tasks. This will get 
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist upload

clean: cleanlinks
	find . -name "*.pyc" |xargs rm || true
	rm -r homestead || true
	rm -r dist || true
	rm -r build || true
	rm -r *.egg-info || true
	rm tiddlyweb.log || true
	rm -r store || true
	rm -r tiddlywebplugins/hoster/resources || true

contents:
	./cacher

test: contents
	py.test -x test

dist: test contents
	python setup.py sdist

upload: clean pypi

pypi: test
	python setup.py sdist upload

dev: contents
	./betsy homestead
	(cd homestead &&  ln -s ../tiddlywebplugins . && \
	    ln -s ../tiddlywebplugins/templates . && \
	    ln -s ../manger.py . && \
	    ln -s ../refresh .)
	echo "import mangler" >> tiddlywebconfig.py

cleanlinks:
	rm logout.py twedit.py templates || true
	find tiddlywebplugins -type l |xargs rm ||true
