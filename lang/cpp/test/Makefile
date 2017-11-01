LDFLAGS=-Lgoogletest/googlemock/gtest/ $(shell pkg-config --cflags --libs googletest/gtest.pc)
CXXFLAGS=-g -I.. -Igoogletest/googletest/include
TARGETS=bin/test
all: bin $(TARGETS)

bin/test: test.cpp ../src/messages/MON.h ../src/ParseUBX.h ../src/UBX.h ../src/serializer.h ../src/deserializer.h ./prettyprint.h
	g++ $(LDFLAGS) $(CXXFLAGS) $< -o$@

test: $(TARGETS)
	bin/test

bin:
	mkdir bin

clean:
	rm -f bin/*

.PHONY: test clean
