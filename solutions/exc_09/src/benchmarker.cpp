#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <chrono>
#include "list/array_list.hpp"
#include "list/system_linked_list.hpp"

using namespace std::chrono;

ListBase* choose_list(std::string type, size_t item_size, size_t num_elements) {
    if(type.compare("array") != 0 && type.compare("linked") != 0){
        std::cerr << "Unknown list type: " << type << std::endl;
        return nullptr;
    }

    switch(item_size) {
        case 8:
            if (type.compare("array") == 0) {
                //allocate N+1 as described in the task
                return new ArrayList<8>(num_elements+1);
            } else {
                return new SystemLinkedList<8>();
            }
        case 512:
            if (type.compare("array") == 0) {
                return new ArrayList<512>(num_elements+1);
            } else {
                return new SystemLinkedList<512>();
            }
        case 8000000:
            if (type.compare("array") == 0) {
                return new ArrayList<8000000>(num_elements+1);
            } else {
                return new SystemLinkedList<8000000>();
            }
        default:
            std::cerr << "Unsupported item size: " << item_size << std::endl;
            return nullptr;
    }
}

int convert_value(void* ptr){
    if(ptr == nullptr){
        return -1;
    }

    uint64_t value;
    std::memcpy(&value, static_cast<uint64_t*>(ptr), sizeof(value));
    return value;
}

size_t compute_rw_interval(float rw_percent, size_t total_op){
    size_t rw_portion = static_cast<size_t>(std::round(rw_percent*total_op));
    size_t id_portion = total_op - rw_portion;

    size_t interval = (rw_portion == 0) ? 0: id_portion/rw_portion;
    return interval;
}

void run_benchmark(ListBase* list, size_t total_op, size_t interval, size_t item_size, size_t elem_count){
    bool rw_alternator = true;
    bool id_alternator = true;
    size_t index = 0;
    size_t current_size = elem_count;  // Track actual list size as it changes
    void* tmp = malloc(item_size);
    volatile uint64_t value = 0xAAAAAAAAAAAAAAAAULL;

    for(size_t i = 0; i < total_op; i++){

        // Read/Write Block
        if(i% (interval+1) == interval){
            if(rw_alternator){
                if(current_size > 0 && index < current_size){
                    void* read_result = list->read(index);
                    if(read_result != nullptr){
                        memcpy(tmp, read_result, item_size);
                        // Only XOR up to 8 bytes, or less if item_size is smaller
                        size_t xor_size = (item_size >= 8) ? 8 : item_size;
                        uint64_t xor_val = 0;
                        memcpy(&xor_val, tmp, xor_size);
                        value = value ^ xor_val;
                    }
                }
            }
            else{
                if(current_size > 0 && index < current_size){
                    list->write(index, value);
                }
            }
            rw_alternator = !rw_alternator;
        }

        // Insert/Delete Block
        else{
            if(id_alternator){
                list->insert(index, value);
                current_size++;
            }
            else{
                if(current_size > 0 && index < current_size){
                    list->remove(index);
                    current_size--;
                }
            }
            id_alternator = !id_alternator;
        }
        index = (index + 1) % (current_size > 0 ? current_size : 1);
    }
    free(tmp);
}

void init_list_linear(ListBase* list, size_t elem_count){
    for(size_t i = 0; i < elem_count; i++){
        uint64_t val = (static_cast<uint64_t>(rand()) << 32) | static_cast<uint64_t>(rand());
        list->insert(i, val);
    }
}

void init_list_random(ListBase* list, size_t elem_count){
    //init the list half linear 
    init_list_linear(list, elem_count/2);

    // shuffle the rest
    size_t remaining = (elem_count % 2 == 1) ? (elem_count/2)+1 : elem_count/2;
    for(size_t i = 0; i < remaining; i++){
        size_t max_index = (elem_count/2) + i;
        size_t index = (max_index > 0) ? rand() % (max_index + 1) : 0;
        uint64_t val = (static_cast<uint64_t>(rand()) << 32) | static_cast<uint64_t>(rand());
        list->insert(index, val);
    }
}

bool choose_init_type(std::string method){
    if(method.compare("random")==0){
        return true;
    }
    else if(method.compare("linear")==0){
        return false;
    }
    else{
        std::cerr << "Unknown initialization type, use either 'random' or 'linear'!"<<std::endl;
        exit(EXIT_FAILURE);
    }
}

void init_list(ListBase* list, size_t elem_count, std::string method){
    bool do_random = choose_init_type(method);
    
    if(do_random){
        init_list_random(list, elem_count);
    }
    else{
        init_list_linear(list, elem_count);
    }
}

int main(int argc, char* argv[]){
    if(argc != 7){
        std::cerr << "Usage: " << argv[0] <<
         "<percentage read/write> " <<
         "<total operations> " << 
         "<element count> "<<
         "<item size [8,512,8000000] bytes> " <<
         "<type [linked,array]> "<<
         "<init [linear, random]>" 
         << std::endl;
        return EXIT_FAILURE;
    }
    srand(time(NULL));

    float rw_percent = static_cast<float>(std::stof(argv[1]));
    if(rw_percent < 0.001f){
        std::cerr << "Read/Write percentage to small." << std::endl;
        return EXIT_FAILURE;
    }

    size_t n_operations = static_cast<size_t>(std::stoull(argv[2]));
    size_t element_count = static_cast<size_t>(std::stoull(argv[3]));
    size_t item_size = static_cast<size_t>(std::stoull(argv[4]));


    size_t interval = compute_rw_interval(rw_percent, n_operations);
    ListBase* list = choose_list(argv[5], item_size, element_count);
    init_list(list, element_count, argv[6]);

    auto start = steady_clock::now();
    run_benchmark(list, n_operations, interval, item_size, element_count);
    auto end = steady_clock::now();

    auto duration = duration_cast<microseconds>(end-start);

    //std::cout << "Time elapsed: " << duration.count() << " microseconds" << std::endl;
    std::cout << duration.count() << std::endl;

    delete list;
    return EXIT_SUCCESS;
}
