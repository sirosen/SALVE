###
# distribution and building makefile for SALVE
# Used to bundle up the various setuptools operations needed to do a release
#
# NO ONE SAID THIS WOULD BE PRETTY
# JUST NEEDS TO WORK FOR ME
###

MOVE_LIST=setup.py MANIFEST.in requirements.txt
SETUP_OPTIONS=

.PHONY: copy-files clean distclean

# default target is dev
all: dev

stable: build
dev:
	$(MAKE) build SETUP_OPTIONS="egg_info --tag-build=.dev"

copy-files:
	cp ${MOVE_LIST} ../

clean:
	cd .. && rm -f ${MOVE_LIST}

distclean: clean
	rm -rf ../.setup-venv ../dist ../build ../salve.egg-info

../.setup-venv: requirements.txt
	virtualenv ../.setup-venv
	../.setup-venv/bin/pip install -r requirements.txt

build: copy-files ../.setup-venv
	cd .. && .setup-venv/bin/python setup.py ${SETUP_OPTIONS} sdist bdist_egg
	cd .. && . .setup-venv/bin/activate; twine upload dist/*
	$(MAKE) clean
