LDFLAGS=-Lgoogletest/googlemock/gtest/ $(shell pkg-config --cflags --libs googletest/gtest.pc)
CXXFLAGS=-g -I.. -Igoogletest/googletest/include
TARGETS=bin/test bin/testParseNMEAPayload
DEP=../src/parseUBXBase.h ../src/parseNMEAPayload.h ../src/UBX.h ../src/serializeUBX.h ../src/parseUBX.h
all: bin $(TARGETS)

bin/%:%.cpp $(DEP) ../src/messages/MON.h ./prettyprint.h
	g++ $(LDFLAGS) $(CXXFLAGS) $< -o$@

test: $(TARGETS)
	bin/test
	bin/testParseNMEAPayload

bin:
	mkdir bin

clean:
	rm -rf bin/*

.PHONY: test clean
