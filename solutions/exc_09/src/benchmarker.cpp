#include <cstdlib>
#include <iostream>
#include <string>
#include "list/array_list.hpp"
#include "list/linked_list.hpp"


ListBase* choose_list(std::string type, size_t item_size, size_t num_elements) {
    if(type.compare("array") != 0 && type.compare("linked") != 0){
        std::cerr << "Unknown list type: " << type << std::endl;
        return nullptr;
    }

    switch(item_size) {
        case 1:
            if (type.compare("array") == 0) {
                return new ArrayList<1>(num_elements+1);
            } else {
                return new LinkedList<1>();
            }
        case 512:
            if (type.compare("array") == 0) {
                return new ArrayList<512>(num_elements+1);
            } else {
                return new LinkedList<512>();
            }
        case 8000000:
            if (type.compare("array") == 0) {
                return new ArrayList<8000000>(num_elements+1);
            } else {
                return new LinkedList<8000000>();
            }
        default:
            std::cerr << "Unsupported item size: " << item_size << std::endl;
            return nullptr;
    }
}

char convert_value(void* ptr){
    if(ptr == nullptr){
        return -1;
    }

    char value;
    std::memcpy(&value, static_cast<char*>(ptr), sizeof(char));
    return value;
}


int main(int argc, char* argv[]){
    if(argc != 6){
        std::cerr << "Usage: " << argv[0] << "<percentage read/write> <total operations> <element count> <item size [1,512,8000000]> <[linked,array]>" << std::endl;
        return EXIT_FAILURE;
    }

    float rw_percent = static_cast<float>(std::stof(argv[1]));
    size_t n_operations = static_cast<size_t>(std::stoull(argv[2]));
    size_t element_count = static_cast<size_t>(std::stoull(argv[3]));
    size_t item_size = static_cast<size_t>(std::stoull(argv[4]));

    ListBase* list = choose_list(argv[5], item_size, element_count);

    list->insert(0, '5');

    char test = convert_value(list->read(0));

    std::cout << test << std::endl;

    return EXIT_SUCCESS;
}
