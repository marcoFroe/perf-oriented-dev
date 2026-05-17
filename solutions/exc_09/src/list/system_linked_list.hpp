#include <cstddef>
#include <cstdint>
#include <forward_list>
#include <cstring>
#include "list_base.hpp"

template<size_t StorageSize>
class SystemLinkedList : public ListBase {
    public:
        SystemLinkedList();
        ~SystemLinkedList();
        void* insert(size_t index, uint64_t value) override;
        void remove(size_t index) override;
        void* read(size_t index) override;
        void write(size_t index, uint64_t value) override;
        size_t get_element_size() const override { return StorageSize; }

    private:
        struct Node {
            uint64_t value[StorageSize];
        };
        std::forward_list<Node> list;
};
