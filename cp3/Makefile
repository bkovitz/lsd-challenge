PY = python3.12
# Python libraries that must be installed:
#   lark
#   pyrsistent

ut:
	$(PY) -m unittest -v testTRS.py #Model.py
ut1:	
	$(PY) -m unittest testTRS.TestTRS.test_dollar_sign

tags:
	ctags *.py

.PHONY: tags
