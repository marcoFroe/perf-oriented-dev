#pragma once
#include <cstddef>
#include <cstdint>

class ListBase {
    public:
        virtual ~ListBase() = default;
        virtual void* insert(size_t index, uint64_t value) = 0;
        virtual void remove(size_t index) = 0;
        virtual void* read(size_t index) = 0;
        virtual void write(size_t index, uint64_t value) = 0;
        virtual size_t get_element_size() const = 0;
};
