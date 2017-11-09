all: lang/cpp/src
	./generateCpp.py

tests:
	make -C lang/cpp/ test

lang/cpp/src:
	mkdir -p $<

push:
	git subtree push --prefix lang/cpp https://github.com/mayeranalytics/pyUBX-Cpp.git master

.PHONY: test push
