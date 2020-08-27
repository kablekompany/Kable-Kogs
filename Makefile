PYTHON ?= python3.8

# Python Code Styler oh my giner
reformat:
	$(PYTHON) -m isort --atomic -w 99 .
	$(PYTHON) -m black -l 99 .
stylecheck:
	$(PYTHON) -m isort --atomic -check -w 99 .
	$(PYTHON) -m black --check -l 99 .
stylediff:
	$(PYTHON) -m isort --atomic --check --diff -w 99 .
	$(PYTHON) -m black --check --diff -l 99 .
# seems to be the routine reqs for most creators in this community. Adding isort too
