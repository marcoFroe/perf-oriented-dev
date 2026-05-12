#include <cstddef>
#include <cstring>
#include "list_base.hpp"

template<size_t StorageSize>

class LinkedList : public ListBase {
    public:
        LinkedList();
        ~LinkedList();
        void* insert(size_t index, char value) override;
        void remove(size_t index) override;
        void* read(size_t index) override;
        void write(size_t index, char value) override;
        size_t get_element_size() const override { return StorageSize; }

    private:
        struct Node {
            char value[StorageSize];
            Node* next;
        };
        Node* head;
        size_t node_count;
    };
