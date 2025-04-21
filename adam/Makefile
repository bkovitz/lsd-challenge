PY = python3.13
# Python libraries that must be installed:
#   lark
#   pyrsistent

all: test coverage types docs

test:
<<<<<<< HEAD
	pytest .

coverage: test
	coverage xml

test-cov-html:
	pytest --cov=. --cov-report=html && xdg-open htmlcov/index.html

types:
	pyright lsd/*.py

docs: types
	$(MAKE) -C docs/ html

docs-auto:
	sphinx-autobuild docs docs/_build/html
format:
	isort ./lsd
	black ./lsd

=======
	$(PY) -m pytest *.py
>>>>>>> parent of 15f09df (add commets)
ut:
	$(PY) -m unittest -v test_*.py --failfast
ut1:	
	$(PY) -m unittest testTRS.TestTRS.test_rewrite_subexpression

tags:
	ctags *.py

clean:
	find . -name "__pycache__" -type d -exec rm -r {} +
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache/


zip: clean
	zip -r lsd.zip lsd/ tests/ Makefile pyproject.toml readme.org shell.nix todo.org

.PHONY: tags
