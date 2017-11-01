all: lang/cpp/src
	./generateCpp.py

tests:
	make -C lang/cpp/ test

lang/cpp/src:
	mkdir -p $<

.PHONY: test
