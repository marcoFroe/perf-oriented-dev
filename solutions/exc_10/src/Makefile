CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -O2 -g

all: benchmarker

benchmarker: benchmarker.cpp list/array_list.cpp list/system_linked_list.cpp list/unrolled_linked_list.cpp list/tiered_array.cpp list/array_list.hpp list/system_linked_list.hpp list/list_base.hpp
	$(CXX) $(CXXFLAGS) -o benchmarker benchmarker.cpp list/array_list.cpp list/system_linked_list.cpp list/unrolled_linked_list.cpp list/tiered_array.cpp

clean:
	rm -f benchmarker

.PHONY: all clean
