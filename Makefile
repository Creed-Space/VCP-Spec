PYTHON ?= python3

.PHONY: check validate validate-schemas strict-schemas check-links lint test audits

check: validate strict-schemas lint

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
	$(PYTHON) -m ruff check scripts
	$(PYTHON) scripts/validate_repo.py --only links

test:
	$(PYTHON) scripts/validate_repo.py

audits:
	$(PYTHON) -m pip_audit --requirement requirements-dev.txt
	npm audit --audit-level=moderate
