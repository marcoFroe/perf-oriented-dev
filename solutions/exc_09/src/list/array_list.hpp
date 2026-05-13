#include <cstddef>
#include <cstdint>
#include <cstring>
#include "list_base.hpp"

template<size_t StorageSize>


class ArrayList : public ListBase {
    public:
        ArrayList(size_t size);
        ~ArrayList();
        void* insert(size_t index, uint64_t value) override;
        void remove(size_t index) override;
        void* read(size_t index) override;
        void write(size_t index, uint64_t value) override;
        size_t get_element_size() const override { return StorageSize; }

    private:
        void* storage;
        size_t element_count;
        size_t max_size;

        void* resize_storage();
    };
