
.PHONY: dev-env
dev-env:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt

.PHONY: test
test:
	PYTHONPATH=. pytest -c setup.cfg --cov-report term-missing --junitxml=report.xml

.PHONY: func-test
func-test:
	PYTHONPATH=src python tests/functional/test_wishlist.py

.PHONY: run-local
run-local:
	PYTHONPATH=src uvicorn app:app --reload

.PHONY: build
build:
	docker build -t wishlist:dev .

.PHONY: run
run: build
	docker run --rm --name wishlist-service -d -p 8080:80 wishlist:dev

.PHONY: stop
stop:
	docker stop wishlist-service
