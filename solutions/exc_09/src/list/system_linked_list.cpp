#include <cstdint>
#include <cstring>
#include "system_linked_list.hpp"

template<size_t StorageSize>
SystemLinkedList<StorageSize>::SystemLinkedList() {
}

template<size_t StorageSize>
SystemLinkedList<StorageSize>::~SystemLinkedList() {
}

template<size_t StorageSize>
void* SystemLinkedList<StorageSize>::insert(size_t index, uint64_t value) {
    Node new_node;
    std::memcpy(new_node.value, &value, sizeof(value));

    // Handle insertion at index 0 (beginning)
    if (index == 0) {
        this->list.push_front(new_node);
        return &(this->list.front().value);
    }

    // Find the position before where we want to insert
    auto it = this->list.before_begin();
    auto next = std::next(it);
    size_t current_index = 0;

    while (next != this->list.end() && current_index < index - 1) {
        ++it;
        ++next;
        current_index++;
    }

    // Insert after the found position
    auto result = this->list.insert_after(it, new_node);
    return result->value;
}

template<size_t StorageSize>
void SystemLinkedList<StorageSize>::remove(size_t index) {
    if (index == 0) {
        if (this->list.begin() != this->list.end()) {
            this->list.pop_front();
        }
        return;
    }

    // Find the position before the element to remove
    auto it = this->list.before_begin();
    auto next = std::next(it);
    size_t current_index = 0;

    while (next != this->list.end() && current_index < index - 1) {
        ++it;
        ++next;
        current_index++;
    }

    // Erase the element after the found position
    if (next != this->list.end()) {
        this->list.erase_after(it);
    }
}

template<size_t StorageSize>
void* SystemLinkedList<StorageSize>::read(size_t index) {
    auto it = this->list.begin();
    size_t current_index = 0;

    while (it != this->list.end() && current_index < index) {
        ++it;
        current_index++;
    }

    if (it != this->list.end()) {
        return it->value;
    }

    return nullptr;
}

template<size_t StorageSize>
void SystemLinkedList<StorageSize>::write(size_t index, uint64_t value) {
    auto it = this->list.begin();
    size_t current_index = 0;

    while (it != this->list.end() && current_index < index) {
        ++it;
        current_index++;
    }

    if (it != this->list.end()) {
        std::memcpy(it->value, &value, sizeof(value));
    }
}

// Explicit template instantiation
template class SystemLinkedList<8>;        // 8 bytes
template class SystemLinkedList<512>;      // 512 bytes
template class SystemLinkedList<8000000>;  // 8 MB
