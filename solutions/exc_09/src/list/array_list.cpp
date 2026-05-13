#include "array_list.hpp"
#include <cstdlib>
#include <cstring>

template<size_t StorageSize>
ArrayList<StorageSize>::ArrayList(size_t size){
    this->storage = calloc(size, StorageSize);
    this->element_count = 0;
    this->max_size = size;
}

template<size_t StorageSize>
ArrayList<StorageSize>::~ArrayList(){
    free(this->storage);
}

template<size_t StorageSize>
void* ArrayList<StorageSize>::insert(size_t index, char value){
    if(this->element_count == this->max_size){
        this->storage = resize_storage();
    }
    
    char* char_storage = static_cast<char*>(this->storage);
    
    // Shift elements to the right by StorageSize chars
    char* source = char_storage + (this->element_count - 1) * StorageSize;
    char* dest = char_storage + this->element_count * StorageSize;
    for(size_t i = this->element_count; i > index; i--){
        memmove(dest, source, StorageSize);
        dest -= StorageSize;
        source -= StorageSize;
    }
    
    // Copy the new value at the target index
    memcpy(char_storage + index * StorageSize, &value, sizeof(value));
    this->element_count++;
    
    return char_storage + index * StorageSize;
}

template<size_t StorageSize>
void* ArrayList<StorageSize>::resize_storage(){
    this->max_size = 2*this->max_size;
    this->storage = realloc(this->storage, this->max_size * StorageSize);
    return this->storage;
}

template<size_t StorageSize>
void ArrayList<StorageSize>::remove(size_t index){
    char* char_storage = static_cast<char*>(this->storage);
    
    // Shift elements to the left by StorageSize chars
    for(size_t i = index; i < this->element_count - 1; i++){
        char* source = char_storage + (i + 1) * StorageSize;
        char* dest = char_storage + i * StorageSize;
        memmove(dest, source, StorageSize);
    }
    
    this->element_count--;
}

template<size_t StorageSize>
void* ArrayList<StorageSize>::read(size_t index){
    if(index >= this->element_count){
        return nullptr;
    }
    
    char* char_storage = static_cast<char*>(this->storage);
    return char_storage + index * StorageSize;
}

template<size_t StorageSize>
void ArrayList<StorageSize>::write(size_t index, char value){
    if(index < this->element_count){
        char* char_storage = static_cast<char*>(this->storage);
        memcpy(char_storage + index * StorageSize, &value, sizeof(value));
    }
}

// Explicit template instantiation
template class ArrayList<1>; // 1 Byte
template class ArrayList<512>; // 512 Byte
template class ArrayList<8000000>; // 8 MB 