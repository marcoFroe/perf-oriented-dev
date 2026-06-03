#include "list/array_list.hpp"
#include "list/system_linked_list.hpp"
#include "list/tiered_array.hpp"
#include "list/unrolled_linked_list.hpp"
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <iostream>
#include <ostream>
#include <string>

using namespace std::chrono;

#define TIME_FRAME 2
#define REPEATS 10

struct Xorshift32 {
	uint32_t state = rand(); // Any non-zero seed

	uint32_t operator()() {
		state ^= state << 13;
		state ^= state >> 17;
		state ^= state << 5;
		return state;
	}
};

ListBase* choose_list(std::string type, size_t item_size) {
	if(type.compare("array") != 0 && type.compare("linked") != 0 && type.compare("unrolled") != 0 &&
	   type.compare("tiered") != 0) {
		std::cerr << "Unknown List type supplied! Supported are array, linked, unrolled, tiered."
		          << std::endl;
		exit(EXIT_FAILURE);
	}
	switch(item_size) {
		case 8:
			if(type.compare("array") == 0) {
				return new ArrayList<8>();
			} else if(type.compare("linked") == 0) {
				return new SystemLinkedList<8>();
			} else if(type.compare("unrolled") == 0) {
				return new UnrolledLinkedList<8>();
			} else {
				return new TieredArray<8>();
			}
		case 512:
			if(type.compare("array") == 0) {
				return new ArrayList<512>();
			} else if(type.compare("linked") == 0) {
				return new SystemLinkedList<512>();
			} else if(type.compare("unrolled") == 0) {
				return new UnrolledLinkedList<512>();
			} else {
				return new TieredArray<512>();
			}
		case 8000000:
			if(type.compare("array") == 0) {
				return new ArrayList<8000000>();
			} else if(type.compare("linked") == 0) {
				return new SystemLinkedList<8000000>();
			} else if(type.compare("unrolled") == 0) {
				return new UnrolledLinkedList<8000000>();
			} else {
				return new TieredArray<8000000>();
			}

		default:
			std::cerr << "Unsupported item size: " << item_size << std::endl;
			exit(EXIT_FAILURE);
	}
	return nullptr;
}

int convert_value(void* ptr) {
	if(ptr == nullptr) {
		return -1;
	}

	uint64_t value;
	std::memcpy(&value, static_cast<uint64_t*>(ptr), sizeof(value));
	return value;
}

size_t compute_rw_interval(float rw_percent, size_t total_op) {
	size_t rw_portion = static_cast<size_t>(std::round(rw_percent * total_op));
	size_t id_portion = total_op - rw_portion;

	size_t interval = (rw_portion == 0) ? 0 : id_portion / rw_portion;
	return interval;
}

size_t run_benchmark_linear(ListBase* list, size_t interval, size_t item_size, size_t elem_count) {
	bool rw_alternator = true;
	bool id_alternator = true;
	size_t index = 0;
	void* tmp = malloc(item_size);

	size_t operation_counter = 0;

	auto end = steady_clock::now() + seconds(TIME_FRAME);

	while(steady_clock::now() <= end) {
		// Read/Write Block
		if(operation_counter % (interval + 1) == interval) {
			if(rw_alternator) {
				// Read
				void* read_result = list->read(index);
				if(read_result != nullptr) {
					memcpy(tmp, read_result, item_size);
					// increment data at some random point
					volatile char* storage = static_cast<char*>(tmp);
					storage[5] += '1';
				}
			} else {
				// write
				list->write(index, tmp);
			}
			rw_alternator = !rw_alternator;
		}
		// Insert/Delete Block
		else {
			if(id_alternator) {
				list->insert(index, tmp);
			} else {
				list->remove(index);
			}
			id_alternator = !id_alternator;
		}

		// Rest pointer
		index = (index + 1) % elem_count;
		operation_counter++;
	}

	free(tmp);
	return operation_counter;
}

size_t run_benchmark_random(ListBase* list, size_t interval, size_t item_size, size_t elem_count) {
	bool rw_alternator = true;
	bool id_alternator = true;
	size_t index = 0;
	void* tmp = malloc(item_size);

	size_t operation_counter = 0;

	auto end = steady_clock::now() + seconds(TIME_FRAME);

	Xorshift32 rng;

	while(steady_clock::now() <= end) {
		// Read/Write Block
		if(operation_counter % (interval + 1) == interval) {
			if(rw_alternator) {
				// Read
				void* read_result = list->read(index);
				if(read_result != nullptr) {
					memcpy(tmp, read_result, item_size);
					// increment data at some random point
					volatile char* storage = static_cast<char*>(tmp);
					storage[9] = +1;
				}
			} else {
				// write
				list->write(index, tmp);
			}
			rw_alternator = !rw_alternator;
		}
		// Insert/Delete Block
		else {
			if(id_alternator) {
				list->insert(index, tmp);
			} else {
				list->remove(index);
			}
			id_alternator = !id_alternator;
		}

		// Rest pointer
		index = rng() % elem_count;
		operation_counter++;
	}

	free(tmp);
	return operation_counter;
}

void init_list_linear(ListBase* list, size_t elem_count, size_t item_size) {
	char* data = static_cast<char*>(malloc(item_size));
	for(size_t i = 0; i < elem_count; i++) {
		char val = (static_cast<char>(rand()));
		data[i % item_size] = val;
		list->insert(i, data);
	}
	free(data);
}

void init_list_random(ListBase* list, size_t elem_count, size_t item_size) {
	// init the list half linear
	init_list_linear(list, elem_count / 2, item_size);
	char* data = static_cast<char*>(malloc(item_size));

	// shuffle the rest
	size_t remaining = (elem_count % 2 == 1) ? (elem_count / 2) + 1 : elem_count / 2;
	for(size_t i = 0; i < remaining; i++) {
		size_t max_index = (elem_count / 2) + i;
		size_t index = (max_index > 0) ? rand() % (max_index + 1) : 0;

		char val = (static_cast<char>(rand()));
		data[i % item_size] = val;
		list->insert(index, data);
	}
	free(data);
}

bool choose_type(std::string method) {
	if(method.compare("random") == 0) {
		return true;
	} else if(method.compare("linear") == 0) {
		return false;
	} else {
		std::cerr << "Unknown initialization type, use either 'random' or 'linear'!" << std::endl;
		exit(EXIT_FAILURE);
	}
}

void init_list(ListBase* list, size_t elem_count, std::string method, size_t item_size) {
	bool do_random = choose_type(method);

	if(do_random) {
		init_list_random(list, elem_count, item_size);
	} else {
		init_list_linear(list, elem_count, item_size);
	}
}

int main(int argc, char* argv[]) {
	if(argc != 7) {
		std::cerr << "Usage: " << argv[0] << " <percentage read/write> "
		          << "<element count> " << "<item size [8,512,8000000] bytes> "
		          << "<type [linked,array]> " << "<init [linear, random]> "
		          << "<iter-type [linear, random]>" << std::endl;
		return EXIT_FAILURE;
	}
	srand(time(NULL));

	float rw_percent = static_cast<float>(std::stof(argv[1]));
	if(rw_percent < 0.001f) {
		std::cerr << "Read/Write percentage to small." << std::endl;
		return EXIT_FAILURE;
	}

	size_t element_count = static_cast<size_t>(std::stoull(argv[2]));
	size_t item_size = static_cast<size_t>(std::stoull(argv[3]));

	size_t interval = compute_rw_interval(rw_percent, 2000000);
	ListBase* list = choose_list(argv[4], item_size);
	bool do_random = choose_type(argv[6]);

	init_list(list, element_count, argv[5], item_size);

	if(list == nullptr) {
		std::cerr << "Failed to initialize list!" << std::endl;
		return EXIT_FAILURE;
	}

	size_t counter = 0;

	if(do_random) {
		for(auto i = 0; i < REPEATS; i++) {
			counter += run_benchmark_random(list, interval, item_size, element_count);
		}
	} else {
		for(auto i = 0; i < REPEATS; i++) {
			counter += run_benchmark_linear(list, interval, item_size, element_count);
		}
	}

	std::cout << counter / REPEATS << std::endl;

	delete list;
	return EXIT_SUCCESS;
}