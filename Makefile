# Simple Makefile for some common tasks. This will get 
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist upload

clean: cleanlinks
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r *.egg-info || true
	rm tiddlyweb.log || true
	rm -r store || true
	rm -r tiddlywebplugins/hoster/resources || true

contents:
	./cacher

test:
	py.test -x test

dist: test contents
	python setup.py sdist

upload: clean pypi

pypi: test
	python setup.py sdist upload

devlinks:
	ln -sf ~/src/tiddlyweb-plugins/logout/logout.py .
	ln -sf ~/src/tiddlyweb-plugins/twedit/twedit.py .
	ln -sf ./tiddlywebplugins/templates .

cleanlinks:
	rm logout.py twedit.py templates || true
	find tiddlywebplugins -type l |xargs rm ||true
