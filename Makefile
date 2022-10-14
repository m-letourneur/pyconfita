
all: prod-ready clean-dist build-dist upload-pypi

venv:
	source venv/bin/activate

test: venv
	pip install .
	pip install -r requirements.test.txt
	pytest

fmt: venv
	black tests/ src/

check-fmt: venv
	black tests/ src/ --check

prod-ready: test fmt

check-prod-ready: test check-fmt

clean-dist:
	rm -rf dist

build-dist:
	python -m build

upload-pypi: venv
	twine upload dist/*
