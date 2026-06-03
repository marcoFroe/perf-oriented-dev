#include "array_list.hpp"
#include <cstring> // for memcpy

template <size_t StorageSize> void* ArrayList<StorageSize>::insert(size_t index, void* value) {
	size_t byte_pos = index * StorageSize;
	storage.insert(storage.begin() + byte_pos, StorageSize, 0);
	std::memcpy(&storage[byte_pos], value, StorageSize);
	return &storage[byte_pos];
}

template <size_t StorageSize> void ArrayList<StorageSize>::remove(size_t index) {
	size_t byte_pos = index * StorageSize;
	storage.erase(storage.begin() + byte_pos, storage.begin() + byte_pos + StorageSize);
}

template <size_t StorageSize> void* ArrayList<StorageSize>::read(size_t index) {
	return &storage[index * StorageSize];
}

template <size_t StorageSize> void ArrayList<StorageSize>::write(size_t index, void* value) {
	std::memcpy(&storage[index * StorageSize], value, StorageSize);
}

// Explicit template instantiation
template class ArrayList<8>;       // 8 bytes
template class ArrayList<512>;     // 512 bytes
template class ArrayList<8000000>; // 8 MB
