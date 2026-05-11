CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -O2

all: app

app: main.cpp linked_list.cpp linked_list.hpp
	$(CXX) $(CXXFLAGS) -o app main.cpp linked_list.cpp

clean:
	rm -f app

.PHONY: all clean
