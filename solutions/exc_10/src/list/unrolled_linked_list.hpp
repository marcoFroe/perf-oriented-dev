

#pragma once

#include <cstddef>
#include "list_base.hpp"

#define maxElements 5

template <size_t StorageSize>
class UnrolledLinkedList : public ListBase {
  public:
    UnrolledLinkedList();
    ~UnrolledLinkedList();

    void* insert(size_t index, void* value) override;
    void remove(size_t index) override;
    void* read(size_t index) override;
    void write(size_t index, void* value) override;
    size_t get_element_size() const override { return StorageSize; }

    size_t size() const;

  private:
    static constexpr int nodeCapacity = maxElements;

    struct Node {
        Node() : numElements(0), next(nullptr) {}
        int numElements;
        char data[nodeCapacity * StorageSize];
        Node* next;
    };

    Node* head;
    size_t elementCount;

    Node* findNode(size_t index, size_t& localIndex);
    void splitNode(Node* node);
};

