LDFLAGS=-Lgoogletest/googlemock/gtest/ $(shell pkg-config --cflags --libs googletest/gtest.pc)
CXXFLAGS=-g -I.. -Igoogletest/googletest/include
TARGETS=bin/test bin/testParseNMEA
DEP=../src/parseUBX.h ../src/parseNMEA.h ../src/UBX.h ../src/serializer.h ../src/deserializer.h
all: bin $(TARGETS)

bin/%:%.cpp $(DEP) ../src/messages/MON.h ./prettyprint.h
	g++ $(LDFLAGS) $(CXXFLAGS) $< -o$@

test: $(TARGETS)
	bin/test
	bin/testParseNMEA

bin:
	mkdir bin

clean:
	rm -rf bin/*

.PHONY: test clean
