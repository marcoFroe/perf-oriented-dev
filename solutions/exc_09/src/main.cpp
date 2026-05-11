#include "linked_list.hpp"
#include <cstdlib>
#include <iostream>

int convert_value(void* ptr){
    if(ptr == nullptr){
        return -1;
    }

    int value;
    std::memcpy(&value, static_cast<char*>(ptr), sizeof(int));
    return value;
}

int main(void){
    LinkedList<512> test;

    test.insert(0, 15);
    test.insert(1, 1);
    test.write(0, 45);
    test.remove(0);

    
    std::cout << convert_value(test.read(0)) << std::endl;
    std::cout << convert_value(test.read(1)) << std::endl;

    return EXIT_SUCCESS;
}