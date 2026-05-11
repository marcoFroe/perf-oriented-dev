#include <cstddef>
#include <cstring>

template<size_t StorageSize>

class LinkedList{
    public:
        LinkedList();
        ~LinkedList();
        void* insert(size_t index, int value);
        void remove(size_t index);
        void* read(size_t index);
        void write(size_t index, int value);

    private:
        struct Node {
            char value[StorageSize];
            Node* next;
        };
        Node* head;
        size_t node_count;
    };
