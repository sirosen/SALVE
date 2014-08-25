###
# distribution and building makefile for SALVE
# Used to bundle up the various setuptools operations needed to do a release
#
# NO ONE SAID THIS WOULD BE PRETTY
# JUST NEEDS TO WORK FOR ME
###

SETUP_OPTIONS=

.PHONY: upload clean

# default target is dev
all: dev

stable: upload
dev:
	$(MAKE) upload SETUP_OPTIONS="egg_info --tag-build=.dev"

clean:
	rm -rf ../setup-virtualenv ../dist ../build ../salve.egg-info

../setup-virtualenv: requirements.txt
	virtualenv ../setup-virtualenv
	../setup-virtualenv/bin/pip install -r requirements.txt

build: ../setup-virtualenv
	rm -rf ../dist/ # can't leave this lying around or twine will grab it
	cd .. && setup-virtualenv/bin/python setup.py ${SETUP_OPTIONS} sdist bdist_egg

upload: build
	cd .. && . setup-virtualenv/bin/activate; twine upload dist/*
