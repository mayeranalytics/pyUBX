LDFLAGS=-Lgoogletest/googlemock/gtest/ $(shell pkg-config --cflags --libs googletest/gtest.pc)
CXXFLAGS=-g -O0 -I.. -Igoogletest/googletest/include
TARGETS=bin/testParseUBX bin/testParseNMEA bin/testParse
DEP=../src/parseUBXBase.h ../src/parseNMEABase.h ../src/parseNMEA.h ../src/UBX.h ../src/serializeUBX.h ../src/parseUBX.h ../src/parse.h
all: bin $(TARGETS)

bin/%:%.cpp $(DEP) ../src/messages/MON.h ./prettyprint.h bin
	g++ $(LDFLAGS) $(CXXFLAGS) $< -o$@

test: $(TARGETS)
	bin/testParseUBX
	bin/testParseNMEA
	bin/testParse

bin:
	mkdir bin

clean:
	rm -rf bin/*

.PHONY: test clean
