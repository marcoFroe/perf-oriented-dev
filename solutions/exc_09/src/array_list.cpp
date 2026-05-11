#include "array_list.hpp"
#include <cstdlib>

template<size_t StorageSize>
ArrayList<StorageSize>::ArrayList(){
    storage = malloc(DEFAULTSIZE*sizeof(StorageSize));
    element_count = 0;
}

template<size_t StorageSize>
ArrayList<StorageSize>::~ArrayList(){

}

template<size_t StorageSize>
void* ArrayList<StorageSize>::insert(size_t index, int value){

}

template<size_t StorageSize>
void ArrayList<StorageSize>::remove(size_t index){

}

template<size_t StorageSize>
void* ArrayList<StorageSize>::read(size_t index){

}

template<size_t StorageSize>
void ArrayList<StorageSize>::write(size_t index, int value){

}
