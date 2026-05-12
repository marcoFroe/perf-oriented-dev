CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -O2

all: benchmarker

benchmarker: benchmarker.cpp list/array_list.cpp list/linked_list.cpp list/array_list.hpp list/linked_list.hpp list/list_base.hpp
	$(CXX) $(CXXFLAGS) -o benchmarker benchmarker.cpp list/array_list.cpp list/linked_list.cpp

clean:
	rm -f benchmarker

.PHONY: all clean
