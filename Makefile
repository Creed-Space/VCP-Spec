PYTHON ?= python3

.PHONY: check validate validate-schemas strict-schemas check-links lint test coverage audits

check: coverage validate strict-schemas lint

validate:
	$(PYTHON) scripts/validate_repo.py

validate-schemas:
	$(PYTHON) scripts/validate_repo.py --only schemas
	npm run validate:schemas --silent

strict-schemas:
	npm run validate:schemas --silent

check-links:
	$(PYTHON) scripts/validate_repo.py --only links

lint:
	$(PYTHON) -m ruff check scripts tests

test:
	$(PYTHON) -m unittest discover -s tests -v

coverage:
	$(PYTHON) -m coverage erase
	$(PYTHON) -m coverage run --branch -m unittest discover -s tests -v
	$(PYTHON) -m coverage run --branch --append scripts/validate_repo.py
	$(PYTHON) -m coverage report --include='scripts/validation_utils.py,scripts/protocol_contracts.py,scripts/package_release_candidate.py,scripts/validate_repo.py' --fail-under=80

audits:
	$(PYTHON) -m pip_audit --requirement requirements-dev.txt
	npm audit --audit-level=moderate
