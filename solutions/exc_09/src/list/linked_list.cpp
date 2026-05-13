#include <cstdint>
#include <cstring>
#include "linked_list.hpp"

template<size_t StorageSize>
LinkedList<StorageSize>::LinkedList(){
    head = nullptr;
    node_count = 0;
}

template<size_t StorageSize>
LinkedList<StorageSize>::~LinkedList() {
     if (this->head == nullptr) {
        return;
    }

    Node* current = head->next;
    while (current != head) {
        Node* temp = current;
        current = current->next;
        delete temp;
    }
    delete head;
}


template<size_t StorageSize>
void* LinkedList<StorageSize>::insert(size_t index, uint64_t value) {
    if (index > this->node_count) {
        // Insert at the end
        index = this->node_count; 
    }

    Node* new_node = new Node();
    std::memcpy(new_node->value, &value, sizeof(value));

    if (this->head == nullptr) {
        // First node: make it circular
        this->head = new_node;
        new_node->next = this->head;
    } else if (index == 0) {
        // Insert at head
        Node* last = this->head;
        while (last->next != this->head) {
            last = last->next;
        }
        new_node->next = this->head;
        this->head = new_node;
        last->next = this->head;
    } else {
        // Insert at index or at the end
        Node* current = this->head;
        for (size_t i = 0; i < index - 1; ++i) {
            current = current->next;
        }
        new_node->next = current->next;
        current->next = new_node;
    }

    this->node_count++;
    return new_node->value;
}

template<size_t StorageSize>
void LinkedList<StorageSize>::remove(size_t index) {
    if (this->head == nullptr || index >= this->node_count) {
        return;
    }

    if (index == 0) {
        Node* toDelete = this->head;
        if (this->head->next == this->head) {
            // Only one node in list
            this->head = nullptr;
        } else {
            // Find the last node and move to new head
            Node* last = this->head;
            while (last->next != this->head) {
                last = last->next;
            }
            this->head = this->head->next;
            last->next = this->head;
        }
        delete toDelete;
    } else {
        Node* current = this->head;
        for (size_t i = 0; i < index - 1; ++i) {
            current = current->next;
        }
        Node* toDelete = current->next;
        current->next = toDelete->next;
        delete toDelete;
    }
    this->node_count--;
}

template<size_t StorageSize>
void* LinkedList<StorageSize>::read(size_t index) {
    if (index >= this->node_count || this->head == nullptr) {
        return nullptr;
    }

    Node* current = this->head;
    for (size_t i = 0; i < index; ++i) {
        current = current->next;
    }
    return current->value;
}

template<size_t StorageSize>
void LinkedList<StorageSize>::write(size_t index, uint64_t value){
    if (index >= this->node_count || this->head == nullptr) {
        return;
    }
    
    size_t count = 0;
    Node* current = this->head;
    while(count != index){
        current = current->next;
        count++;
    }
    std::memcpy(current->value, &value, sizeof(value));
}

// Explicit template instantiation 
template class LinkedList<8>; // 1 char
template class LinkedList<512>; // 512 char
template class LinkedList<8000000>; // 8 MB 
