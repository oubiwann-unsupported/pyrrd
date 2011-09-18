clean:
	find ./ -name "*~" -exec rm {} \;
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;
	find . -name "*.sw[op]" -exec rm {} \;
	rm -rf MSG.backup _trial_temp/ build/ dist/ MANIFEST \
		CHECK_THIS_BEFORE_UPLOAD.txt *.egg-info


stat:
	@echo "Changes:"
	@cat MSG
	@echo
	@echo "Bazzar working dir status:"
	@echo
	@echo -n "Current revision: "
	@bzr revno
	@bzr stat


# XXX this target isn't working...
todo:
	@echo `find .|xargs grep -2 XXX`


build:
	python setup.py build
	python setup.py sdist


check-docs: files = "README"
check-docs:
	@python -c \
	"from pyrrd.testing import suite;suite.runDocTests('$(files)');"


check-examples: files = "examples/*.py"
check-examples:
	@python -c \
	"from pyrrd.testing import suite;suite.runDocTests('$(files)');"

check-dist:
	@echo "Need to fill this in ..."


check: build check-docs check-examples
	@python -c \
	"from pyrrd.testing import runner;runner.main();"

build-docs:
	cd docs/sphinx; make html

commit: check
	bzr commit --show-diff


commit-msg: check
	bzr commit --file=MSG


push: commit clean
	bzr push lp:pyrrd


push-msg: commit-msg clean
	bzr push lp:pyrrd
	mv MSG MSG.backup
	touch MSG

register:
	python setup.py register

upload: check
	python setup.py sdist upload --show-response

upload-docs: build-docs
	python setup.py upload_docs --upload-dir=docs/html/
